import { useEffect } from 'react'
import '../styles/globals.css'

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
      import('@sentry/browser').then((Sentry) => {
        Sentry.init({ dsn: process.env.NEXT_PUBLIC_SENTRY_DSN })
      }).catch(()=>{})
    }
  }, [])

  return <Component {...pageProps} />
}

export default MyApp
