import numpy as np
import mujoco
import time
from mujoco import viewer
import matplotlib.pyplot as plt

model = mujoco.MjModel.from_xml_path("mujoco_menagerie/unitree_go1/scene.xml")

# Initialize simulation.
data = mujoco.MjData(model)
mujoco.mj_resetData(model, data)


print(mujoco.__version__)


duration = 3.8  # (seconds)
framerate = 60  # (Hz)
timestep = 1 / framerate  # (seconds)


states_legend = np.array([None for _ in range(data.qpos.shape[0])])
# Print the association of qpos entries with joint names
for i in range(model.njnt):
    joint_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i)
    qpos_index = model.jnt_qposadr[i]
    print(f"Joint '{joint_name}' starts at qpos index {qpos_index}")
    states_legend[qpos_index] = joint_name
    
# Simulate and display video.
states = []
with mujoco.viewer.launch_passive(model, data) as viewer:

    start = time.time()
    while viewer.is_running() and time.time() - start < duration:
        step_start = time.time()

        # mj_step can be replaced with code that also evaluates
        # a policy and applies a control signal before stepping the physics.
        # Apply random actions
        random_actions = np.random.uniform(-1, 1, size=model.nu)  # Random control inputs
        data.ctrl[:] = random_actions
        
        states.append(data.qpos[:].copy())
        mujoco.mj_step(model, data)

        # Example modification of a viewer option: toggle contact points every two seconds.
        with viewer.lock():
            viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(data.time % 2)

        # Pick up changes to the physics state, apply perturbations, update options from GUI.
        viewer.sync()

        # Rudimentary time keeping, will drift relative to wall clock.
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)


# Plot the states
states = np.array(states)
plt.plot(states)
plt.legend(states_legend)
plt.show()
