import { useState } from 'react'

export default function ProductDetail({ product, onBack, onAddToCart }) {
  const [qty, setQty]     = useState(1)
  const [added, setAdded] = useState(false)

  if (!product) return null
  const stars   = Math.round(product.rating)
  const savings = product.price_original ? product.price_original - product.price : 0

  const handleAdd = () => {
    onAddToCart?.(product, qty)
    setAdded(true)
    setTimeout(() => setAdded(false), 1800)
  }

  return (
    <div className="h-full flex flex-col overflow-y-auto">
      <button onClick={onBack} className="flex items-center gap-1 text-brand text-sm font-medium mb-4 hover:underline">
        ← Back to catalogue
      </button>

      <div className="flex gap-6 flex-wrap">
        <div className="w-48 h-48 rounded-2xl flex items-center justify-center flex-shrink-0 overflow-hidden"
             style={{ background: 'rgba(13,92,110,0.05)' }}>
          {product.image
            ? <img src={product.image} alt={product.name} className="w-full h-full object-contain p-2" />
            : <span className="text-8xl">{product.emoji || '📦'}</span>}
        </div>

        <div className="flex-1 min-w-48">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h2 className="text-xl font-bold text-gray-800 leading-tight">{product.name}</h2>
            {product.in_stock
              ? <span className="text-xs bg-green-50 text-green-700 border border-green-200 rounded-full px-2 py-0.5 whitespace-nowrap">✓ In Stock</span>
              : <span className="text-xs bg-red-50 text-red-600 rounded-full px-2 py-0.5">Out of Stock</span>
            }
          </div>

          <div className="flex items-center gap-1 mb-3">
            <span className="text-yellow-400">{'★'.repeat(stars)}{'☆'.repeat(5 - stars)}</span>
            <span className="text-gray-500 text-sm">{product.rating} ({product.review_count} reviews)</span>
          </div>

          <div className="flex items-baseline gap-3 mb-2">
            <span className="text-3xl font-bold text-gray-900">${product.price.toLocaleString()}</span>
            {product.price_original > product.price && (
              <>
                <span className="text-gray-400 line-through">${product.price_original.toLocaleString()}</span>
                <span className="text-coral font-semibold">Save ${savings.toLocaleString()}!</span>
              </>
            )}
          </div>

          {product.discount_pct > 0 && (
            <div className="inline-block bg-coral text-white text-xs font-bold px-3 py-1 rounded-full mb-3">
              {product.discount_pct}% OFF — Limited Time
            </div>
          )}

          <p className="text-gray-600 text-sm leading-relaxed mb-4">{product.description}</p>

          {/* Add to cart controls */}
          {product.in_stock && onAddToCart && (
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center gap-2 border border-gray-200 rounded-xl px-2 py-1.5">
                <button onClick={() => setQty(q => Math.max(1, q - 1))}
                  className="w-6 h-6 rounded-full bg-gray-100 text-sm flex items-center justify-center hover:bg-gray-200 transition">−</button>
                <span className="text-sm font-medium w-6 text-center">{qty}</span>
                <button onClick={() => setQty(q => q + 1)}
                  className="w-6 h-6 rounded-full bg-gray-100 text-sm flex items-center justify-center hover:bg-gray-200 transition">+</button>
              </div>
              <button
                onClick={handleAdd}
                className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  added
                    ? 'bg-green-50 text-green-600 border border-green-200'
                    : 'text-white hover:opacity-90'
                }`}
                style={added ? {} : { background: '#0D5C6E' }}
              >
                {added ? '✓ Added to Cart!' : `Add ${qty > 1 ? `${qty}x ` : ''}to Cart`}
              </button>
            </div>
          )}

          {product.pdf_url && (
            <a href={product.pdf_url} target="_blank" rel="noreferrer"
               className="inline-flex items-center gap-1.5 text-xs font-medium text-brand border border-brand rounded-lg px-3 py-1.5 hover:bg-brand hover:text-white transition-colors">
              📄 Download Spec Sheet (PDF)
            </a>
          )}
        </div>
      </div>

      {product.highlights?.length > 0 && (
        <div className="mt-5">
          <h3 className="font-semibold text-gray-700 mb-2">Key Highlights</h3>
          <div className="grid grid-cols-2 gap-2">
            {product.highlights.map((h, i) => (
              <div key={i} className="flex items-start gap-2 bg-brand/5 rounded-xl p-3 text-sm text-gray-700">
                <span className="text-brand mt-0.5">✓</span><span>{h}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {product.specs && (
        <div className="mt-5">
          <h3 className="font-semibold text-gray-700 mb-2">Specifications</h3>
          <div className="rounded-xl border border-gray-100 overflow-hidden">
            {Object.entries(product.specs).map(([k, v], i) => (
              <div key={k} className={`flex px-4 py-2.5 text-sm ${i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                <span className="w-44 text-gray-500 font-medium flex-shrink-0">{k}</span>
                <span className="text-gray-800">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
