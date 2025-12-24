import useSWR from 'swr'

const fetcher = (url) => fetch(url).then(r => r.json())

export default function Cars(){
  const {data, error} = useSWR('/api/proxy/cars', fetcher)
  if(error) return <div>Failed to load</div>
  if(!data) return <div>Loading...</div>
  return (
    <main style={{padding:20}}>
      <h1>Cars</h1>
      <ul>
        {data.map(c => (
          <li key={c.id} style={{marginBottom:10}}>
            <strong>{c.make} {c.model}</strong> - ${c.base_monthly_price} {' '}
            <a href={`/quote/${c.id}`}>Get Quote</a>
            <div>
              {c.images && c.images[0] && (
                <img src={`${process.env.NEXT_PUBLIC_API_URL}${c.images[0].url}`} style={{height:60, marginTop:8}} alt="car" />
              )}
            </div>
          </li>
        ))}
      </ul>
    </main>
  )
}
