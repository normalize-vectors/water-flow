class Interpolate():

    def __init__(self, x2, x1, y2, y1):
        """
        Linearly interpolate between two points. Instantiate to ready the object, then call with an x value.

        x values outside of the two points return as though they were on the nearest point.

        Initialization parameters
        ----------
        x: list, length of 2
        y: list, length of 2
            corresponding x and y values of the two points to interpolate between.

        Call parameters
        ----------
        x : float
            x value along the line between the points (x2,y2) and (x1,y1) to evaluate for y.

        Returns
        -------
        float
            Returns y.

        """
        self.x2 = x2
        self.x1 = x1

        self.y2 = y2
        self.y1 = y1

        self.m = (y2 - y1)/(x2 - x1)
        self.b = y2-self.m*x2

    def __call__(self, x):
        if x >= self.x1:
            if x <= self.x2:
                return self.m*x + self.b
            else:
                return self.y2
        else:
            return self.y1


if __name__ == "__main__":

    r = Interpolate(
        x2=30,
        x1=0,
        y2=255,
        y1=0
    )

    b = Interpolate(
        x2=30,
        x1=0,
        y2=0,
        y1=255
    )

    print(b(31))
