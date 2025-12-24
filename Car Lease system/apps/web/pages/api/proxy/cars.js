export default async function handler(req, res){
  // Simple proxy to backend for dev
  const r = await fetch(process.env.NEXT_PUBLIC_API_URL + '/api/v1/cars')
  const data = await r.json()
  res.status(200).json(data)
}
