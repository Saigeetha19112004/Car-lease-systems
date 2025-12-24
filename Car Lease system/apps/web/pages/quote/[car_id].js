import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'

export default function QuotePage(){
  const router = useRouter()
  const { car_id } = router.query
  const [car, setCar] = useState(null)
  const [term, setTerm] = useState(36)
  const [mileage, setMileage] = useState(10000)
  const [down, setDown] = useState(0)
  const [msg, setMsg] = useState('')

  useEffect(()=>{
    if(!car_id) return
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cars/${car_id}`)
      .then(r=>r.json())
      .then(setCar)
      .catch(()=>setCar(null))
  },[car_id])

  async function handleGetQuote(){
    setMsg('Creating quote...')
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/quotes`, {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ car_id, term_months: term, mileage_allowance: mileage, down_payment: down })
    })
    const quote = await res.json()
    setMsg('Accepting quote and creating lease...')
    const acceptRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/quotes/${quote.id}/accept`, { method: 'POST' })
    const acceptJson = await acceptRes.json()
    setMsg('Redirecting to checkout...')
    router.push(`/checkout/${acceptJson.lease_id}`)
  }

  return (
    <main style={{padding:20}}>
      <h1>Get Quote</h1>
      {car ? (
        <div>
          <p><strong>{car.year} {car.make} {car.model}</strong></p>
          <p>Base monthly price: ${car.base_monthly_price}</p>
          <label>Term (months): <input type="number" value={term} onChange={e=>setTerm(Number(e.target.value))} /></label>
          <br />
          <label>Mileage allowance: <input type="number" value={mileage} onChange={e=>setMileage(Number(e.target.value))} /></label>
          <br />
          <label>Down payment: <input type="number" value={down} onChange={e=>setDown(Number(e.target.value))} /></label>
          <br />
          <button onClick={handleGetQuote}>Get Quote & Create Lease</button>
          <p>{msg}</p>
        </div>
      ) : (
        <p>Loading car...</p>
      )}
    </main>
  )
}
