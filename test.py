l_thigh_vector = standard_vector(self.thigh_length)
        l_knee = r_hip + rotate_vector_by_quaternion(r_thigh_vector, self.r_thigh_quat)
        r_leg_vector = standard_vector(self.lower_leg_length)

        r_ankle = r_knee + rotate_vector_by_quaternion(r_leg_vector, self.r_leg_quat)

        r_q_thigh_conj = quaternion_conjugate(self.r_thigh_quat)
        r_q_rel = quaternion_multiply(self.r_leg_quat, r_q_thigh_conj)
        _, r_knee_angle = quaternion_to_axis_angle(r_q_rel)

        print("Effective right knee rotation angle (radians):", r_knee_angle)
        print("Effective right knee rotation angle (degrees):", 360 - np.degrees(r_knee_angle))

        # Plot the segments as lines
        self.ax.plot([r_hip[0], r_knee[0]], [r_hip[1], r_knee[1]], [r_hip[2], r_knee[2]], 'r-', lw=3, label="R Thigh")
        self.ax.plot([r_knee[0], r_ankle[0]], [r_knee[1], r_ankle[1]], [r_knee[2], r_ankle[2]], 'g-', lw=3, label="R Lower Leg")