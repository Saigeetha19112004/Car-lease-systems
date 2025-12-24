import Link from 'next/link'
export default function Home(){
  return (
    <main style={{padding:20}}>
      <h1>Car Lease System (MVP)</h1>
      <p><Link href="/cars">Browse Cars</Link></p>
    </main>
  )
}
