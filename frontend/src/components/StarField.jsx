// StarField – decorative animated background used on the Landing page
import { useMemo } from 'react'

function StarField() {
  const stars = useMemo(() => {
    return Array.from({ length: 160 }, (_, i) => ({
      id: i,
      top:   `${Math.random() * 100}%`,
      left:  `${Math.random() * 100}%`,
      size:  `${Math.random() * 2 + 0.5}px`,
      dur:   `${2 + Math.random() * 4}s`,
      delay: `${Math.random() * 4}s`,
    }))
  }, [])

  return (
    <div className="star-field" aria-hidden="true">
      {stars.map(s => (
        <div
          key={s.id}
          className="star"
          style={{
            top: s.top,
            left: s.left,
            width: s.size,
            height: s.size,
            '--dur': s.dur,
            '--delay': s.delay,
          }}
        />
      ))}
    </div>
  )
}

export default StarField
