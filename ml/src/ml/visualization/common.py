from dataclasses import dataclass


@dataclass
class VariableInfo:
    label: str
    units: str


KNOWN_VARIABLES = {
    "vor": VariableInfo(label="Vorticity", units="$s^{-1}$"),
    "stream": VariableInfo(label="Streamfunction", units="$m^2 s^{-1}$"),
    "ucomp": VariableInfo(label="Zonal Wind", units="$m s^{-1}$"),
    "vcomp": VariableInfo(label="Meridional Wind", units="$m s^{-1}$"),
}


def resolve_variable_info(variable_name: str, variable_info: VariableInfo = None) -> VariableInfo:
    if variable_info:
        return variable_info
    if variable_name not in KNOWN_VARIABLES:
        raise ValueError(
            f"variable {variable_name} has no known variable info definition and none was provided. "
            "either provide a variable_info, or define a new known variable"
        )
    return KNOWN_VARIABLES[variable_name]
