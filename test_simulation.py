import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# Define segment lengths
L_thigh = 0.4  # meters
L_shin = 0.4  # meters
L_foot = 0.2  # meters


def compute_leg_positions(theta_k, theta_a):
    """
    Compute 3D positions of the knee, ankle, and foot based on joint angles.
    """
    # Hip is fixed at (0,0,0)
    hip = np.array([0, 0, 0])

    # Knee position (assume thigh is along Y-axis initially)
    knee = hip + np.array([0, L_thigh * np.cos(theta_k), -L_thigh * np.sin(theta_k)])

    # Ankle position (shin rotates from knee, with added lift)
    ankle = knee + np.array([0, L_shin * np.cos(theta_a), -L_shin * np.sin(theta_a)])

    # Foot position (flat along ground for simplicity)
    foot = ankle + np.array([0, 0, L_foot])

    return hip, knee, ankle, foot


def update(frame, lines):
    """Update function for animation."""
    # Simulated motion (step-like trajectory)
    A = np.pi / 6  # Max knee angle
    f = 0.05  # Frequency of step

    theta_k = A * np.sin(2 * np.pi * f * frame)  # Knee oscillation
    theta_a = np.pi / 12 * np.sin(2 * np.pi * f * frame)  # Ankle oscillation

    # Add ankle lifting for stepping effect
    ankle_lift = 0.1 * max(0, np.sin(np.pi * f * frame))  # Lift only in swing phase

    hip, knee, ankle, foot = compute_leg_positions(theta_k, theta_a, ankle_lift)

    # Update line positions
    lines[0].set_data([hip[0], knee[0]], [hip[1], knee[1]])
    lines[0].set_3d_properties([hip[2], knee[2]])

    lines[1].set_data([knee[0], ankle[0]], [knee[1], ankle[1]])
    lines[1].set_3d_properties([knee[2], ankle[2]])

    lines[2].set_data([ankle[0], foot[0]], [ankle[1], foot[1]])
    lines[2].set_3d_properties([ankle[2], foot[2]])

    return lines


def visualize_leg_motion():
    """Create a 3D animation of the lower leg motion."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_zlim(-0.5, 0.5)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # Initial lines
    (line1,) = ax.plot([], [], [], "r", linewidth=3)  # Thigh
    (line2,) = ax.plot([], [], [], "g", linewidth=3)  # Shin
    (line3,) = ax.plot([], [], [], "b", linewidth=3)  # Foot

    ani = animation.FuncAnimation(
        fig, update, frames=100, fargs=([line1, line2, line3],), interval=50
    )
    plt.show()


# Run visualization
visualize_leg_motion()
