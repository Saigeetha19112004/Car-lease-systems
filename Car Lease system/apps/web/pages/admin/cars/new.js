import { useState } from 'react'
import { useRouter } from 'next/router'

export default function NewCar(){
  const [form, setForm] = useState({ make:'', model:'', year:2024, base_monthly_price:0 })
  const router = useRouter()
  async function handle(){
    const token = localStorage.getItem('auth-token')
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cars`, { method:'POST', headers: {'Content-Type':'application/json', 'Authorization': `Bearer ${token}`}, body: JSON.stringify(form) })
    if(res.ok){
      router.push('/admin/cars')
    }
  }
  return (
    <main style={{padding:20}}>
      <h1>Create Car</h1>
      <input placeholder="make" value={form.make} onChange={e=>setForm({...form, make:e.target.value})} />
      <br />
      <input placeholder="model" value={form.model} onChange={e=>setForm({...form, model:e.target.value})} />
      <br />
      <input placeholder="year" type="number" value={form.year} onChange={e=>setForm({...form, year:Number(e.target.value)})} />
      <br />
      <input placeholder="monthly" type="number" value={form.base_monthly_price} onChange={e=>setForm({...form, base_monthly_price:Number(e.target.value)})} />
      <br />
      <button onClick={handle}>Create</button>
    </main>
  )
}
