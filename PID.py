class PID:
    """
    Proportional-Integral-Derivative (PID) controller.

    Args:
        P (float): Proportional gain.
        I (float): Integral gain.
        D (float): Derivative gain.
        lim (float, optional): Output limit. Defaults to 1.

    Attributes:
        P (float): Proportional gain.
        I (float): Integral gain.
        D (float): Derivative gain.
        e_prec (float): Previous error.
        iE (float): Integral of the error.
        lim (float): Output limit.

    Methods:
        update(e, dt): Update the PID controller and calculate the control signal.
        clear(): Reset the PID controller.

    """

    def init(self, P, I, D, lim=1):
        self.P = P
        self.I = I
        self.D = D
        self.e_prec = 0
        self.iE = 0
        self.lim = lim

    def update(self, e, dt):
        """
        Update the PID controller and calculate the control signal.

        Args:
            e (float): Error signal.
            dt (float): Time step.

        Returns:
            float: Control signal.

        """
        P = self.P
        D = self.D
        I = self.I
        u = P * e + D * (e - self.e_prec) / dt + I * self.iE
        self.e_prec = e
        self.iE += e * dt
        self.iE = (
            self.lim
            if self.iE > self.lim
            else (-self.lim if self.iE < -self.lim else self.iE)
        )

        return u

    def clear(self):
        """
        Reset the PID controller.

        """
        self.e_prec = 0
        self.iE = 0