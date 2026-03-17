from typing import List
import pandas as pd
import datetime as dt
from .grouping import recursive_grouping

try:
    # python-toon (modulo: toon)
    from toon import encode as _toon_encode
except ImportError:
    try:
        # toons (modulo: toons)
        import toons as _toons

        def _toon_encode(data):
            return _toons.dumps(data)

    except ImportError as exc:
        raise ImportError(
            "Nenhuma biblioteca TOON instalada. Instale 'toons' ou 'python-toon'."
        ) from exc

def encode_toon(
    df: pd.DataFrame, 
    name: str, 
    datetimes: List[str] = None, 
    columns_agrupation: List[str] = None
) -> str:
    if (datetimes == None):
        datetimes = []
    
    for datetime in datetimes:
        if (datetime in df.columns):
            df[datetime] = pd.to_datetime(df[datetime], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    
    if columns_agrupation:
        valid_columns = [col for col in columns_agrupation if col in df.columns]
        return _toon_encode({name: recursive_grouping(df, valid_columns)})

    return _toon_encode({name: df.copy().to_dict(orient="records")})