from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
from sqlmodel import Session, select
from ...models.models import Car, CarImage
from ...db.session import engine
from ...services.images import save_image_file
from ...dependencies import admin_required

router = APIRouter()

@router.post("/", response_model=Car)
def create_car(car: Car, user=Depends(admin_required)):
    with Session(engine) as session:
        session.add(car)
        session.commit()
        session.refresh(car)
        return car

@router.put("/{car_id}", response_model=Car)
def update_car(car_id: str, car: Car, user=Depends(admin_required)):
    with Session(engine) as session:
        existing = session.get(Car, car_id)
        if not existing:
            raise HTTPException(status_code=404, detail='Car not found')
        for k, v in car.dict(exclude_unset=True).items():
            setattr(existing, k, v)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

@router.delete("/{car_id}")
def delete_car(car_id: str, user=Depends(admin_required)):
    with Session(engine) as session:
        existing = session.get(Car, car_id)
        if not existing:
            raise HTTPException(status_code=404, detail='Car not found')
        session.delete(existing)
        session.commit()
        return {'deleted': True}

@router.get("/")
def list_cars(make: Optional[str] = None, model: Optional[str] = None, year_min: Optional[int] = None, year_max: Optional[int] = None, price_min: Optional[float] = None, price_max: Optional[float] = None, status: Optional[str] = None, page: int = 1, per_page: int = 20):
    with Session(engine) as session:
        q = select(Car)
        if make:
            q = q.where(Car.make == make)
        if model:
            q = q.where(Car.model == model)
        if year_min:
            q = q.where(Car.year >= year_min)
        if year_max:
            q = q.where(Car.year <= year_max)
        if price_min:
            q = q.where(Car.base_monthly_price >= price_min)
        if price_max:
            q = q.where(Car.base_monthly_price <= price_max)
        if status:
            q = q.where(Car.status == status)
        offset = (page - 1) * per_page
        cars = session.exec(q.offset(offset).limit(per_page)).all()
        # attach images
        result = []
        for car in cars:
            images = session.exec(select(CarImage).where(CarImage.car_id == car.id)).all()
            car_dict = car.dict()
            car_dict['images'] = [{'id':str(i.id), 'url': f'/api/v1/media/images/{i.url}', 'is_primary': i.is_primary} for i in images]
            result.append(car_dict)
        return result

@router.get("/{car_id}")
def get_car(car_id: str):
    with Session(engine) as session:
        car = session.get(Car, car_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        images = session.exec(select(CarImage).where(CarImage.car_id == car.id)).all()
        # return car + images
        car_dict = car.dict()
        car_dict['images'] = [{'id':str(i.id), 'url': f'/api/v1/media/images/{i.url}', 'is_primary': i.is_primary} for i in images]
        return car_dict

@router.post("/{car_id}/images")
def upload_car_image(car_id: str, file: UploadFile = File(...), is_primary: Optional[bool] = Form(False), user=Depends(admin_required)):
    with Session(engine) as session:
        car = session.get(Car, car_id)
        if not car:
            raise HTTPException(status_code=404, detail='Car not found')
        filename, thumb = save_image_file(file)
        img = CarImage(car_id=car.id, url=filename, is_primary=is_primary)
        if is_primary:
            # unset other primary images for this car
            others = session.exec(select(CarImage).where(CarImage.car_id == car.id, CarImage.is_primary == True)).all()
            for o in others:
                o.is_primary = False
                session.add(o)
        session.add(img)
        session.commit()
        session.refresh(img)
        return {'image_id': img.id, 'url': f"/api/v1/media/images/{filename}", 'is_primary': img.is_primary}

@router.post("/{car_id}/images/{image_id}/set-primary")
def set_primary_image(car_id: str, image_id: str, user=Depends(admin_required)):
    with Session(engine) as session:
        car = session.get(Car, car_id)
        if not car:
            raise HTTPException(status_code=404, detail='Car not found')
        img = session.get(CarImage, image_id)
        if not img or str(img.car_id) != str(car.id):
            raise HTTPException(status_code=404, detail='Image not found')
        # unset others
        others = session.exec(select(CarImage).where(CarImage.car_id == car.id, CarImage.is_primary == True)).all()
        for o in others:
            o.is_primary = False
            session.add(o)
        img.is_primary = True
        session.add(img)
        session.commit()
        session.refresh(img)
        return {'image_id': img.id, 'is_primary': img.is_primary}

@router.delete("/{car_id}/images/{image_id}")
def delete_image(car_id: str, image_id: str, user=Depends(admin_required)):
    from ...services.images import delete_image_file
    with Session(engine) as session:
        car = session.get(Car, car_id)
        if not car:
            raise HTTPException(status_code=404, detail='Car not found')
        img = session.get(CarImage, image_id)
        if not img or str(img.car_id) != str(car.id):
            raise HTTPException(status_code=404, detail='Image not found')
        # delete files
        delete_image_file(img.url)
        session.delete(img)
        session.commit()
        return {'deleted': True}
