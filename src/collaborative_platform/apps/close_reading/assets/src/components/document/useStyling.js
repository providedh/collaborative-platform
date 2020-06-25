import { useEffect } from 'react'

export default function (container, documentResponse, preferences) {
  useEffect(() => {
    console.log(container, documentResponse, preferences)
  }, [container, documentResponse])
}
