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
      className={`rounded-2xl border-2 p-3 cursor-pointer transition-all duration-300 hover:shadow-md bg-white flex flex-col ${
        highlighted ? 'border-brand shadow-lg scale-105' : 'border-gray-100 hover:border-gray-200'
      }`}
      style={highlighted ? { borderColor: '#0D5C6E', boxShadow: '0 0 0 3px rgba(13,92,110,0.15)' } : {}}
    >
      <div className="w-full h-24 rounded-xl flex items-center justify-center text-5xl mb-2 relative overflow-hidden"
           style={{ background: highlighted ? 'rgba(13,92,110,0.05)' : '#f9fafb' }}>
        {product.image
          ? <img src={product.image} alt={product.name} className="w-full h-full object-contain p-1"
                 onError={e => { e.target.style.display='none'; e.target.nextSibling.style.display='flex' }} />
          : null}
        <span style={{ display: product.image ? 'none' : 'flex' }}>{product.emoji || '📦'}</span>
        {discount > 0 && (
          <div className="absolute top-1.5 right-1.5 bg-red-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-lg">
            -{discount}%
          </div>
        )}
      </div>

      {product.brand && (
        <p className="text-xs text-gray-400 font-medium uppercase tracking-wide mb-0.5 truncate">{product.brand}</p>
      )}

      <h3 className="font-semibold text-gray-800 text-xs leading-snug line-clamp-2 mb-1.5 flex-1">
        {product.name}
      </h3>

      {topHighlight && (
        <div className="flex items-center gap-1 mb-2">
          <span className="text-brand text-xs">✓</span>
          <span className="text-xs text-gray-500 truncate">{topHighlight}</span>
        </div>
      )}

      <div className="flex items-center gap-1 mb-2">
        <span className="text-yellow-400 text-xs">{'★'.repeat(stars)}{'☆'.repeat(5 - stars)}</span>
        <span className="text-gray-400 text-xs">({product.review_count})</span>
        {energyRating && (
          <span className="ml-auto text-xs font-bold px-1.5 py-0.5 rounded"
                style={{ background: ENERGY_COLORS[energyRating] + '22', color: ENERGY_COLORS[energyRating] }}>
            {energyRating}★ Energy
          </span>
        )}
      </div>

      <div className="flex items-baseline gap-1.5 mb-2">
        <span className="text-base font-bold text-gray-900">${product.price.toLocaleString()}</span>
        {product.price_original > product.price && (
          <span className="text-xs text-gray-400 line-through">${product.price_original.toLocaleString()}</span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <span className={`text-xs font-medium ${product.in_stock ? 'text-green-600' : 'text-red-500'}`}>
          {product.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
        </span>
        {highlighted && !onAddToCart && (
          <span className="text-xs text-brand font-semibold">⭐ Recommended</span>
        )}
      </div>

      {onAddToCart && product.in_stock && (
        <button
          onClick={handleAddToCart}
          className={`mt-2 w-full py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
            added
              ? 'bg-green-50 text-green-600 border border-green-200'
              : 'bg-brand/10 text-brand border border-brand/20 hover:bg-brand hover:text-white'
          }`}
        >
          {added ? '✓ Added to Cart' : '+ Add to Cart'}
        </button>
      )}
    </div>
  )
}
