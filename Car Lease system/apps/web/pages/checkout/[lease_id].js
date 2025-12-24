import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'

export default function CheckoutPage(){
  const router = useRouter()
  const { lease_id } = router.query
  const [loaded, setLoaded] = useState(false)
  const [lease, setLease] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(()=>{
    if(!lease_id) return
    // fetch lease
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/leases/${lease_id}`)
      .then(r=>r.json())
      .then(setLease)
      .catch(()=>setLease(null))
  },[lease_id])

  useEffect(()=>{
    if(!lease_id) return
    const addScript = () => {
      if(window.paypal) return Promise.resolve()
      return new Promise((resolve, reject)=>{
        const s = document.createElement('script')
        s.src = `https://www.paypal.com/sdk/js?client-id=${process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID}&currency=USD`
        s.onload = ()=>resolve()
        s.onerror = ()=>reject()
        document.body.appendChild(s)
      })
    }

    addScript().then(()=>{
      if(!window.paypal) return
      setLoaded(true)
      window.paypal.Buttons({
        createOrder: async function(data, actions){
          const amount = lease ? lease.total_amount : (window.prompt('Enter amount to pay') || '0')
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/payments/create-order`,{
            method: 'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ lease_id: lease_id, amount: parseFloat(amount), currency: 'USD' })
          })
          const dataJson = await res.json()
          return dataJson.order_id
        },
        onApprove: async function(data, actions){
          try{
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/payments/capture`,{
              method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ order_id: data.orderID })
            })
            const json = await res.json()
            setMessage('Payment captured successfully')
          }catch(e){
            setMessage('Error capturing payment')
          }
        },
        onError: function(err){
          console.error(err)
          setMessage('Payment error')
        }
      }).render('#paypal-buttons')
    }).catch(()=>setMessage('Failed to load PayPal SDK'))

  },[lease_id, lease])

  return (
    <main style={{padding:20}}>
      <h1>Checkout</h1>
      {lease ? (
        <div>
          <p><strong>Lease:</strong> {lease.lease_number}</p>
          <p><strong>Amount:</strong> {lease.total_amount} USD</p>
        </div>
      ) : (
        <p>Loading lease...</p>
      )}
      <div id="paypal-buttons" style={{marginTop:20}} />
      {message && <p>{message}</p>}
    </main>
  )
}
