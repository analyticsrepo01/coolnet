import { useState } from 'react'

const ENERGY_COLORS = { 5: '#16a34a', 4: '#65a30d', 3: '#ca8a04', 2: '#ea580c', 1: '#dc2626' }

export default function ProductCard({ product, highlighted, onSelect, onAddToCart }) {
  const [added, setAdded] = useState(false)
  const stars        = Math.round(product.rating)
  const discount     = product.discount_pct
  const energyRating = product.energy_rating
  const topHighlight = product.highlights?.[0]

  const handleAddToCart = (e) => {
    e.stopPropagation()
    onAddToCart?.(product, 1)
    setAdded(true)
    setTimeout(() => setAdded(false), 1800)
  }

  return (
    <div
      onClick={() => onSelect?.(product)}
      className={`rounded-2xl border-2 p-3 cursor-pointer transition-all duration-300 hover:shadow-lg bg-white flex flex-col ${
        highlighted ? 'border-brand shadow-xl scale-105' : 'border-gray-100 hover:border-gray-300'
      }`}
      style={highlighted ? { borderColor: '#0D5C6E', boxShadow: '0 0 0 3px rgba(13,92,110,0.15)' } : {}}
    >
      {/* Image area — taller, gradient bg */}
      <div
        className="w-full h-36 rounded-xl flex items-center justify-center text-5xl mb-3 relative overflow-hidden"
        style={{
          background: highlighted
            ? 'linear-gradient(135deg, rgba(13,92,110,0.08) 0%, rgba(13,92,110,0.03) 100%)'
            : 'linear-gradient(135deg, #f3f4f6 0%, #e9ecef 100%)',
        }}
      >
        {product.image
          ? <img src={product.image} alt={product.name} className="w-full h-full object-contain p-2"
                 onError={e => { e.target.style.display='none'; e.target.nextSibling.style.display='flex' }} />
          : null}
        <span style={{ display: product.image ? 'none' : 'flex' }}>{product.emoji || '📦'}</span>

        {discount > 0 && (
          <div className="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full shadow-sm">
            -{discount}%
          </div>
        )}
        {highlighted && (
          <div className="absolute top-2 left-2 text-xs font-bold px-2 py-0.5 rounded-full text-white shadow-sm"
               style={{ background: '#0D5C6E' }}>
            ⭐ Top Pick
          </div>
        )}
      </div>

      {/* Brand — more prominent */}
      {product.brand && (
        <p className="text-xs font-bold uppercase tracking-widest mb-1 truncate"
           style={{ color: '#0D5C6E' }}>{product.brand}</p>
      )}

      <h3 className="font-semibold text-gray-800 text-sm leading-snug line-clamp-2 mb-2 flex-1">
        {product.name}
      </h3>

      {topHighlight && (
        <div className="flex items-center gap-1 mb-2">
          <span className="text-xs font-bold" style={{ color: '#0D5C6E' }}>✓</span>
          <span className="text-xs text-gray-500 truncate">{topHighlight}</span>
        </div>
      )}

      <div className="flex items-center gap-1 mb-2">
        <span className="text-yellow-400 text-xs">{'★'.repeat(stars)}{'☆'.repeat(5 - stars)}</span>
        <span className="text-gray-400 text-xs">({product.review_count})</span>
        {energyRating && (
          <span className="ml-auto text-xs font-bold px-1.5 py-0.5 rounded-full"
                style={{ background: ENERGY_COLORS[energyRating] + '22', color: ENERGY_COLORS[energyRating] }}>
            {energyRating}★ Energy
          </span>
        )}
      </div>

      <div className="flex items-baseline gap-1.5 mb-2">
        <span className="text-lg font-bold text-gray-900">${product.price.toLocaleString()}</span>
        {product.price_original > product.price && (
          <span className="text-xs text-gray-400 line-through">${product.price_original.toLocaleString()}</span>
        )}
      </div>

      <div className="flex items-center justify-between mb-1">
        <span className={`text-xs font-medium ${product.in_stock ? 'text-green-600' : 'text-red-500'}`}>
          {product.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
        </span>
      </div>

      {onAddToCart && product.in_stock && (
        <button
          onClick={handleAddToCart}
          className={`mt-2 w-full py-2 rounded-xl text-xs font-semibold transition-all duration-200 ${
            added
              ? 'bg-green-50 text-green-600 border border-green-200'
              : 'text-white hover:opacity-90'
          }`}
          style={added ? {} : { background: '#0D5C6E' }}
        >
          {added ? '✓ Added to Cart' : '+ Add to Cart'}
        </button>
      )}
    </div>
  )
}
