import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'

export default function EditCar(){
  const router = useRouter()
  const { id } = router.query
  const [car, setCar] = useState(null)
  const [file, setFile] = useState(null)

  useEffect(()=>{
    if(!id) return
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cars/${id}`).then(r=>r.json()).then(setCar)
  },[id])

  async function handleUpload(){
    const token = localStorage.getItem('auth-token')
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cars/${id}/images`, { method:'POST', body: fd, headers: {'Authorization': `Bearer ${token}`} })
    if(res.ok){
      alert('uploaded')
      window.location.reload()
    }else{
      alert('upload failed')
    }
  }

  if(!car) return <div>Loading...</div>
  return (
    <main style={{padding:20}}>
      <h1>Edit {car.make} {car.model}</h1>
      <p>Monthly: {car.base_monthly_price}</p>
      <div>
        <h3>Images</h3>
        <ul>
          {(car.images||[]).map(img => (
            <li key={img.id} style={{marginBottom:10}}>
              <img src={`${process.env.NEXT_PUBLIC_API_URL}${img.url}`} alt="" style={{height:80}} />
              <div>
                <button onClick={async ()=>{
                  const token = localStorage.getItem('auth-token')
                  const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cars/${id}/images/${img.id}/set-primary`, { method:'POST', headers: {'Authorization': `Bearer ${token}`} })
                  if(r.ok) window.location.reload()
                }}>Set primary</button>
                <button onClick={async ()=>{
                  if(!confirm('Delete image?')) return
                  const token = localStorage.getItem('auth-token')
                  const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cars/${id}/images/${img.id}`, { method:'DELETE', headers: {'Authorization': `Bearer ${token}`} })
                  if(r.ok) window.location.reload()
                }}>Delete</button>
              </div>
            </li>
          ))}
        </ul>
        <input type="file" onChange={e=>setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Upload</button>
      </div>
    </main>
  )
}
