import math, json
import numpy as np
from datetime import datetime, UTC
from scipy.spatial.transform import Rotation as R


class Body:
    # body types
    BARYCENTRE = 1
    PLANET = 2
    STAR = 3

    def __init__(self, entry: dict):
        if entry["type"] == "Barycentre":
            self.type = self.BARYCENTRE
        elif entry["type"] == "Planet":
            self.type = self.PLANET
        elif entry["type"] == "Star":
            self.type = self.STAR
        else:
            raise ValueError("not a body")

        self.bodyID:    int = entry.get("bodyId")
        self.bodyName:  str = entry.get("name")
        self.timestamp = datetime.fromisoformat(entry.get("updateTime")).replace(tzinfo=UTC)

        self.ascendingNode: float = entry.get("ascendingNode", 0.0)
        self.axialTilt:     float = entry.get("axialTilt", 0.0)
        self.eccentricity:  float = entry.get("orbitalEccentricity", 0.0)
        self.orbitalInclination: float = entry.get("orbitalInclination", 0.0)
        self.meanAnomaly:   float = entry.get("meanAnomaly", 0.0)
        self.orbitalPeriod: float = entry.get("orbitalPeriod", 0.0)
        self.periapsis:     float = entry.get("argOfPeriapsis", 0.0)
        self.semiMajorAxis: float = entry.get("semiMajorAxis", 0.0)
        self.orbit:         Orbit = Orbit(self)

        self.parentIDs: list[int] = list()
        for j in entry.get("parents", []):
            for _, id in j.items():
                self.parentIDs.append(id)

class Orbit:
    def __init__(self, body: Body):
        self.isValid = (body.type == Body.BARYCENTRE  or  body.orbitalPeriod != 0.0)
        self.semiMajorAxis =    body.semiMajorAxis
        self.eccentricity =     body.eccentricity
        self.inclination =      body.orbitalInclination
        self.ascendingNode =    body.ascendingNode
        self.argOfPeriapsis =   body.periapsis
        self.meanAnomaly =      body.meanAnomaly
        self.scanTimestamp =    body.timestamp
        self.orbitalPeriod =    body.orbitalPeriod

        # Keplerize
        self.ascendingNode =  (360.0 - self.ascendingNode) % 360.0
        self.argOfPeriapsis = (360.0 - self.argOfPeriapsis) % 360.0

        # ради тестов
        self.meanAnomaly = self.getCurrentMeanAnomaly()

        #rotations
        self.getParentFrameOfReference, self.fromOrbitToGlobal = self.getRotations(body.axialTilt)

    def getRotations(self, axial_tilt):
        axis           = rotate_along(np.array([1, 0, 0]), np.array([0, 0, 1]), self.argOfPeriapsis + self.ascendingNode)
        ascending_node = rotate_along(np.array([1, 0, 0]), np.array([0, 0, 1]), self.ascendingNode)

        r1 = get_rotation(np.array([0, 0, 1]), self.argOfPeriapsis + self.ascendingNode)
        r2 = get_rotation(axis, -axial_tilt)
        r3 = get_rotation(ascending_node, -self.inclination)
        return r3 * r2 * r1, r3 * r1

    def getCurrentMeanAnomaly(self) -> float:
        # this object has moved since the last scan
        diff = (datetime.now(UTC) - self.scanTimestamp).total_seconds()
        if self.semiMajorAxis == 0.0:
            return self.meanAnomaly

        currentMeanAnomaly = self.meanAnomaly + (360.0 * diff / self.orbitalPeriod)
        return currentMeanAnomaly


def find_mean_anomaly(e: float, eccentric: float):
    a = eccentric - (e * math.sin(eccentric))
    return a


def find_eccentric_anomaly(e: float, mean: float, epsilon: float = 1e-6):
    mean = math.radians(mean)
    e_n = mean

    # Newton's methon to find E on given M
    diff = find_mean_anomaly(e, e_n) - mean
    i = 0
    while abs(diff) > epsilon and i < 100:
        e_n1 = e * math.sin(e_n) + mean
        e_n = e_n1
        diff = find_mean_anomaly(e, e_n) - mean
        i += 1

    return e_n

def get_rotation(axis, theta):
    return R.from_rotvec(axis * theta, degrees = True)

def rotate_along(vector: np.array, axis: np.array, theta: float):
    rotation = R.from_rotvec(axis * theta, degrees = True)
    ret = rotation.apply(vector)
    return ret

class Coordinates:
    allBodies: dict[int, Body] = dict()     # key = bodyID

    def transform_to_parent_frame_of_reference(self, coords: np.array, parentIDs: list[int]):
        if len(parentIDs) == 0:
            return coords

        parentID = parentIDs[0]
        if parentID == 0:
            return coords

        parent = self.allBodies.get(parentID)
        if parent == None or parent.bodyID == 0:
            return coords

        coords = parent.orbit.getParentFrameOfReference.apply(coords)

        return self.transform_to_parent_frame_of_reference(coords, parentIDs[1:])


    def calculate_coordinates(self, orbit: Orbit):
        coords = np.zeros(3)
        if not orbit.isValid:
            return coords

        ecc = find_eccentric_anomaly(orbit.eccentricity, orbit.meanAnomaly)

        # 1. Orbit, XY plane, periapsis +X
        coords[0] = math.cos(ecc) - orbit.eccentricity
        coords[1] = math.sqrt(1 - pow(orbit.eccentricity, 2)) * math.sin(ecc)
        coords[2] = 0

        coords = orbit.fromOrbitToGlobal.apply(coords)
        coords *= orbit.semiMajorAxis

        return coords


    def summarize_coordinates(self, body: Body):
        def summarize(bodyID, parentIDs: list[int]):
            if bodyID == 0 or bodyID not in self.allBodies:
                return np.zeros(3)

            orbit = self.allBodies[bodyID].orbit
            coords = self.calculate_coordinates(orbit)
            coords = self.transform_to_parent_frame_of_reference(coords, parentIDs)

            if len(parentIDs) > 1:
                summ = summarize(parentIDs[0], parentIDs[1:])
                coords += summ

            return coords

        return summarize(body.bodyID, body.parentIDs)

    def get_coordinates(self, bodyID):
        body = self.allBodies[bodyID]
        coords = self.summarize_coordinates(body)
        return coords

    def get_all_coordinates(self):
        for bodyID in self.allBodies:
            body = self.allBodies[bodyID]

    def __init__(self, bodies):
        self.allBodies.clear()

        for entry in bodies:
            body = Body(entry)
            self.allBodies[body.bodyID] = body

