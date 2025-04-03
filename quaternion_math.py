import numpy as np


def quaternion_multiply(q1, q2):
    # Multiply two quaternions: q1 * q2
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array(
        [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ]
    )


def rotate_vector_by_quaternion(v, q):
    # Ensure q is a unit quaternion
    q = q / np.linalg.norm(q)

    # Conjugate of quaternion q: q* = (w, -x, -y, -z)
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])

    # Convert vector v into a pure quaternion: (0, v_x, v_y, v_z)
    v_quat = np.concatenate(([0], v))

    # Rotate: v' = q * v_quat * q_conj
    rotated = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)

    # The rotated vector is the vector part of the resulting quaternion
    return rotated[1:]


def normalize(v):
    return v / np.linalg.norm(v)


def quaternion_from_axis_angle(axis, angle_rad):
    axis = normalize(axis)
    s = np.sin(angle_rad / 2)
    w = np.cos(angle_rad / 2)
    return np.array([w, axis[0] * s, axis[1] * s, axis[2] * s])


def rotate_quaternion_by_quaternion(vq, q):
    # Ensure q is a unit quaternion
    q = q / np.linalg.norm(q)

    # Conjugate of quaternion q: q* = (w, -x, -y, -z)
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])

    # Convert vector v into a pure quaternion: (0, v_x, v_y, v_z)

    rotated = quaternion_multiply(quaternion_multiply(q, vq), q_conj)

    # The rotated vector is the vector part of the resulting quaternion
    return rotated


def standard_vector(d):
    return np.array([d, 0, 0])


def quaternion_conjugate(q):
    """Return the conjugate of a quaternion."""
    w, x, y, z = q
    return np.array([w, -x, -y, -z])


def quaternion_to_axis_angle(q):
    """Convert a normalized quaternion to an axis-angle representation."""
    # Ensure q is normalized
    q = q / np.linalg.norm(q)
    w, x, y, z = q
    angle = 2 * np.arccos(w)
    s = np.sqrt(1 - w**2)
    if s < 1e-8:
        # If s is close to zero, return an arbitrary axis
        return np.array([1, 0, 0]), 0
    axis = np.array([x, y, z]) / s
    return axis, angle
