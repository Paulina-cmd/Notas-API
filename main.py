from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="API de Notas",
    description="Una API simple para gestión de notas",
    version="1.0.0"
)

class NotaBase(BaseModel):
    titulo: str
    contenido: str
    autor: str
    categoria: Optional[str] = "General"
    importante: Optional[bool] = False

class NotaCreate(NotaBase):
    pass

class Nota(NotaBase):
    fecha_creacion: datetime
    fecha_actualizacion: datetime

# Almacenamiento en memoria
notas_db = []

# GET - Obtener todas las notas
@app.get("/notas", response_model=List[Nota])
async def obtener_notas(
    categoria: Optional[str] = None,
    importante: Optional[bool] = None
):
    """Obtener todas las notas con filtros opcionales"""
    notas_filtradas = notas_db.copy()
    
    if categoria:
        notas_filtradas = [n for n in notas_filtradas if n.categoria.lower() == categoria.lower()]
    
    if importante is not None:
        notas_filtradas = [n for n in notas_filtradas if n.importante == importante]
    
    return notas_filtradas

# GET - Obtener una nota por título
@app.get("/notas/{titulo}", response_model=Nota)
async def obtener_nota(titulo: str):
    """Obtener una nota específica por título"""
    for nota in notas_db:
        if nota.titulo.lower() == titulo.lower():
            return nota
    
    raise HTTPException(status_code=404, detail="Nota no encontrada")

# POST - Crear nueva nota
@app.post("/notas", response_model=Nota, status_code=201)
async def crear_nota(nota: NotaCreate):
    """Crear una nueva nota"""
    if not nota.titulo.strip():
        raise HTTPException(status_code=400, detail="El título es requerido")
    
    if not nota.contenido.strip():
        raise HTTPException(status_code=400, detail="El contenido es requerido")
    
    # Verificar si ya existe una nota con el mismo título
    for nota_existente in notas_db:
        if nota_existente.titulo.lower() == nota.titulo.lower():
            raise HTTPException(status_code=400, detail="Ya existe una nota con ese título")
    
    fecha_actual = datetime.now()
    
    nueva_nota = Nota(
        titulo=nota.titulo,
        contenido=nota.contenido,
        autor=nota.autor,
        categoria=nota.categoria,
        importante=nota.importante,
        fecha_creacion=fecha_actual,
        fecha_actualizacion=fecha_actual
    )
    
    notas_db.append(nueva_nota)
    return nueva_nota

# PUT - Actualizar nota
@app.put("/notas/{titulo}", response_model=Nota)
async def actualizar_nota(titulo: str, nota_actualizada: NotaCreate):
    """Actualizar una nota existente"""
    for i, nota in enumerate(notas_db):
        if nota.titulo.lower() == titulo.lower():
            
            # Verificar si el nuevo título ya existe (y no es el mismo que estamos actualizando)
            if nota_actualizada.titulo.lower() != titulo.lower():
                for nota_existente in notas_db:
                    if (nota_existente.titulo.lower() == nota_actualizada.titulo.lower() and 
                        nota_existente.titulo.lower() != titulo.lower()):
                        raise HTTPException(status_code=400, detail="Ya existe una nota con ese título")
            
            nota_actualizada_obj = Nota(
                titulo=nota_actualizada.titulo,
                contenido=nota_actualizada.contenido,
                autor=nota_actualizada.autor,
                categoria=nota_actualizada.categoria,
                importante=nota_actualizada.importante,
                fecha_creacion=nota.fecha_creacion,
                fecha_actualizacion=datetime.now()
            )
            
            notas_db[i] = nota_actualizada_obj
            return nota_actualizada_obj
    
    raise HTTPException(status_code=404, detail="Nota no encontrada")

# DELETE - Eliminar nota
@app.delete("/notas/{titulo}")
async def eliminar_nota(titulo: str):
    """Eliminar una nota"""
    for i, nota in enumerate(notas_db):
        if nota.titulo.lower() == titulo.lower():
            nota_eliminada = notas_db.pop(i)
            return {
                "mensaje": "Nota eliminada exitosamente",
                "nota_eliminada": nota_eliminada
            }
    
    raise HTTPException(status_code=404, detail="Nota no encontrada")

# GET - Buscar notas
@app.get("/buscar/{texto}")
async def buscar_notas(texto: str):
    """Buscar notas por título o contenido"""
    resultados = []
    texto_lower = texto.lower()
    
    for nota in notas_db:
        if (texto_lower in nota.titulo.lower() or 
            texto_lower in nota.contenido.lower()):
            resultados.append(nota)
    
    return resultados

# GET - Obtener estadísticas
@app.get("/estadisticas")
async def obtener_estadisticas():
    """Obtener estadísticas de las notas"""
    total_notas = len(notas_db)
    notas_importantes = len([n for n in notas_db if n.importante])
    categorias = {}
    
    for nota in notas_db:
        categorias[nota.categoria] = categorias.get(nota.categoria, 0) + 1
    
    return {
        "total_notas": total_notas,
        "notas_importantes": notas_importantes,
        "notas_normales": total_notas - notas_importantes,
        "categorias": categorias
    }

# Endpoint raíz
@app.get("/")
async def root():
    return {"mensaje": "Bienvenido a la API de Notas"}

# Para ejecutar: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    