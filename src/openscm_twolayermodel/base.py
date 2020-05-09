import pint


class Model:
    @staticmethod
    def _check_is_pint_quantity(quantity, name):
        if not isinstance(quantity, pint.Quantity):
            raise TypeError("{} must be a pint.Quantity".format(name))
