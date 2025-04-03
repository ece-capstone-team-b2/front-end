import time
import numpy as np
import pyvista as pv
from threading import Thread


def create_cylinder_between_points(A, B, radius=0.1):
    """
    Creates a cylinder mesh between two points A and B with the given radius.

    Parameters:
        A (iterable): Starting point (x, y, z).
        B (iterable): Ending point (x, y, z).
        radius (float): Radius of the cylinder.

    Returns:
        pyvista.PolyData: Cylinder mesh.
    """
    A = np.array(A)
    B = np.array(B)
    # Compute the center as the midpoint between A and B
    center = (A + B) / 2.0
    # Direction vector from A to B
    direction = B - A
    height = np.linalg.norm(direction)
    if height == 0:
        raise ValueError("Points A and B are identical. Cannot form a cylinder.")
    # Normalize the direction vector
    direction = direction / height
    return pv.Cylinder(center=center, direction=direction, radius=radius, height=height)


# Initial positions
hip = [0, 0, 0]
knee = [0, -1, 0.2]
ankle = [0, -2, 0.3]
toe = [0.3, -2.2, 0.3]

# Create initial meshes for each segment
thigh_mesh = create_cylinder_between_points(hip, knee, radius=0.15)
lower_leg_mesh = create_cylinder_between_points(knee, ankle, radius=0.12)
foot_mesh = create_cylinder_between_points(ankle, toe, radius=0.08)

# Create a PyVista plotter and add the initial meshes
plotter = pv.Plotter()
thigh_actor = plotter.add_mesh(thigh_mesh, color="red", opacity=0.8, show_edges=True)
lower_leg_actor = plotter.add_mesh(
    lower_leg_mesh, color="green", opacity=0.8, show_edges=True
)
foot_actor = plotter.add_mesh(foot_mesh, color="blue", opacity=0.8, show_edges=True)
plotter.add_axes()


def update_scene(thing):
    """
    Update the cylinder meshes with new positions.
    Replace the simulated new positions with your serial data.
    """
    interactor_state = plotter.iren.get_interactor_style().__getstate__()
    if interactor_state != 0:
        # User is interacting; skip updating for now.
        return
    # --- Simulated serial data update ---
    # In a real application, you would replace these with serial reads.
    new_knee = [0, -1 + 0.1 * np.random.randn(), 0.2 + 0.1 * np.random.randn()]
    new_ankle = [0, -2 + 0.1 * np.random.randn(), 0.3 + 0.1 * np.random.randn()]
    new_toe = [0.3, -2.2 + 0.1 * np.random.randn(), 0.3 + 0.1 * np.random.randn()]
    # -------------------------------------

    # Recompute the cylinder meshes with the new positions
    new_thigh = create_cylinder_between_points(hip, new_knee, radius=0.15)
    new_lower_leg = create_cylinder_between_points(new_knee, new_ankle, radius=0.12)
    new_foot = create_cylinder_between_points(new_ankle, new_toe, radius=0.08)

    # Update the existing actors by replacing their mesh data
    thigh_actor.mapper.SetInputData(new_thigh)
    lower_leg_actor.mapper.SetInputData(new_lower_leg)
    foot_actor.mapper.SetInputData(new_foot)

    # Notify the mappers that the input data has changed
    thigh_actor.mapper.Modified()
    lower_leg_actor.mapper.Modified()
    foot_actor.mapper.Modified()

    # Render the updated scene
    plotter.render()


# Add a callback to update the scene every 1000 milliseconds (1 second)
plotter.add_timer_event(max_steps=100000000, duration=1000, callback=update_scene)

# Start the interactive plot
plotter.show()
