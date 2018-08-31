def a(param1, param2):
    """Jakaś niepotrzebna funkcja.

    Args:
        param1 (int): niepotrzebny pierwszy argument
        param2 (str): niepotrzebny drugi argument

    Returns:
        str: nic ciekawego
    """

    return "nothing special"


class KlasaA(object):
    """Klasa A i tyle."""

    def fun_a(self):
        """fun a"""
        return 1


class KlasaAA:
    """Klasa AA, która po niczym nie dziedziczy."""

    def fun_aaaaaa(self, a, b):
        """Funckja aaaaaaaaaaaa...

        Args:
            a: argument a
            b: argument b

        Returns:
            str: nic
        """

        return "nic"


def funkcja_z_klasa():
    """Ta funkcja zawiera klasę.

    Returns:
        KlasaWFunkcji: instancja tej wewnętrznej klasy.
    """

    class KlasaWFunkcji(object):
        """
        Klasa wewnątrz funkcji :func:`funkcja_z_klasa`.
        """

    return KlasaWFunkcji()
