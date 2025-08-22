from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class RipleyResponse(BaseModel):
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
    transfer_on_order_u: Optional[int] = Field(None, alias="Transfer. on Order(u)")
    transfer_on_order_pesos: Optional[float] = Field(
        None, alias="Transfer. on Order($)"
    )
    stock_on_hand_disponible_u: Optional[int] = Field(
        None, alias="Stock on Hand Disponible (u)"
    )
    stock_on_hand_disponible_pesos: Optional[float] = Field(
        None, alias="Stock on Hand Disponible ($)"
    )
    costo_de_venta_pesos: Optional[float] = Field(None, alias="Costo De Venta($)")
    mark_up: Optional[float] = Field(None, alias="Mark-up")
    marca: Optional[str] = Field(None, alias="Marca")
    temp: Optional[str] = Field(None, alias="Temp.")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"


class RipleyCredentials(BaseModel):
    class TypeReport(str, Enum):
        sales = "ventas"
        stock = "stock"

    username: str
    password: str
    type_report: TypeReport


class RipleyRequestCredentials(BaseModel):
    username: str
    password: str


class StockResponseRipley(BaseModel):
    sucursal: Optional[str]
    marca: Optional[str]
    dpto: Optional[str]
    linea: Optional[str]
    cod_art_ripley: Optional[str]
    desc_art_ripley: Optional[str]
    cod_art_prov_case_pack: Optional[str]
    desc_art_prov_case_pack: Optional[str]
    transfer_on_order_u: Optional[float]
    transfer_on_order_pesos: Optional[float]
    stock_on_hand_disponible_u: Optional[int]
    stock_on_hand_disponible_pesos: Optional[float]
    stock_on_hand_empresa_u: Optional[int]
    stock_on_hand_empresa_pesos: Optional[float]
    stock_protegido_u: Optional[int]
    stock_pdte_por_oc_u: Optional[int]
