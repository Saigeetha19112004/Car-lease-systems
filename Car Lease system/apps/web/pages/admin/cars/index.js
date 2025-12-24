import Link from 'next/link'
import useSWR from 'swr'

const fetcher = (url)=>fetch(url).then(r=>r.json())

export default function AdminCars(){
  const {data, error} = useSWR(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cars`, fetcher)
  if(error) return <div>Error</div>
  if(!data) return <div>Loading...</div>
  return (
    <main style={{padding:20}}>
      <h1>Admin Cars</h1>
      <p><Link href="/admin/cars/new">Create new car</Link></p>
      <ul>
        {data.map(c => (
          <li key={c.id}>
            {c.year} {c.make} {c.model} - ${c.base_monthly_price}
            <Link href={`/admin/cars/${c.id}`} style={{marginLeft:10}}>Edit</Link>
          </li>
        ))}
      </ul>
    </main>
  )
}
