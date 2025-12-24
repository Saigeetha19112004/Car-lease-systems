import { useRouter } from 'next/router'
import { useState } from 'react'

export default function Login(){
  const [email,setEmail] = useState('')
  const [password,setPassword] = useState('')
  const router = useRouter()
  async function handle(){
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email,password})})
    const data = await res.json()
    if(data.access_token){
      localStorage.setItem('auth-token', data.access_token)
      router.push('/admin/cars')
    }
  }
  return (
    <main style={{padding:20}}>
      <h1>Admin Login</h1>
      <input placeholder="email" value={email} onChange={e=>setEmail(e.target.value)} />
      <br />
      <input placeholder="password" value={password} onChange={e=>setPassword(e.target.value)} type="password" />
      <br />
      <button onClick={handle}>Login</button>
    </main>
  )
}
