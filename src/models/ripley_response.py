from typing import Optional
from pydantic import BaseModel, Field


class RipleyResponse(BaseModel):
    fecha: Optional[str] = Field(None, alias="Fecha")
    cod_art_ripley: Optional[int] = Field(None, alias="Cód.Art. Ripley")
    upc: Optional[str] = Field(None, alias="UPC")
    desc_art_ripley: Optional[str] = Field(None, alias="Desc.Art. Ripley")
    cod_art_prov_case_pack: Optional[str] = Field(
        None, alias="Cód.Art.Prov. (Case Pack)"
    )
    desc_art_prov_case_pack: Optional[str] = Field(
        None, alias="Desc.Art.Prov.(Case Pack)"
    )
    sucursal: Optional[str] = Field(None, alias="Sucursal")
    venta_u: Optional[int] = Field(None, alias="Venta (u)")
    venta_pesos: Optional[float] = Field(None, alias="Venta ($)")
    costo_de_venta_pesos: Optional[float] = Field(None, alias="Costo De Venta($)")
    mark_up: Optional[int] = Field(None, alias="Mark-up")
    marca: Optional[str] = Field(None, alias="Marca")
    temp: Optional[str] = Field(None, alias="Temp.")
    unnamed_13: Optional[str] = Field(None, alias="Unnamed: 13")
    unnamed_14: Optional[str] = Field(None, alias="Unnamed: 14")
    unnamed_15: Optional[str] = Field(None, alias="Unnamed: 15")

    class Config:
        allow_population_by_field_name = True
        # Permitir campos adicionales que no estén definidos
        extra = "allow"
