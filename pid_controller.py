class PID:
    """Simple PID control."""

    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        self.setpoint = setpoint  # Desired value
        self.integral = 0  # Integral term
        self.previous_error = 0  # Previous error

    def update(self, measured_value, dt):
        """
        Calculate PID output value for given reference input and feedback.

        :param measured_value: The current value of the variable being controlled
        :param dt: Time interval in seconds
        :return: The control variable
        """
        error = self.setpoint - measured_value
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt

        # Calculate PID output
        output = self.kp * error + self.ki * self.integral + self.kd * derivative

        # Update previous error
        self.previous_error = error

        return output