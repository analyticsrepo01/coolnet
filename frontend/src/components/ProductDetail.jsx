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
      <button onClick={onBack} className="flex items-center gap-1 text-sm font-medium mb-4 hover:underline"
              style={{ color: '#0D5C6E' }}>
        ← Back to catalogue
      </button>

      {/* Hero image banner */}
      <div className="w-full h-56 rounded-2xl relative flex items-center justify-center mb-5 overflow-hidden"
           style={{ background: 'linear-gradient(135deg, #f0f9fb 0%, #e0eef2 100%)' }}>
        {product.image
          ? <img src={product.image} alt={product.name} className="h-full w-full object-contain p-6" />
          : <span className="text-9xl">{product.emoji || '📦'}</span>}

        {/* Sale badge top-left */}
        {product.discount_pct > 0 && (
          <div className="absolute top-3 left-3 bg-red-500 text-white text-sm font-bold px-3 py-1 rounded-full shadow">
            SALE {product.discount_pct}% OFF
          </div>
        )}

        {/* Energy star badge top-right */}
        {product.energy_rating && (
          <div className="absolute top-3 right-3 bg-green-600 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow flex items-center gap-1">
            ⚡ {product.energy_rating}★ Energy
          </div>
        )}
      </div>

      {/* Brand + name + rating + price */}
      <div className="mb-4">
        {product.brand && (
          <p className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color: '#0D5C6E' }}>
            {product.brand}
          </p>
        )}
        <h2 className="text-2xl font-bold text-gray-900 leading-tight mb-2">{product.name}</h2>

        {/* Rating row */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-yellow-400 text-base">{'★'.repeat(stars)}{'☆'.repeat(5 - stars)}</span>
          <span className="text-gray-500 text-sm">{product.rating} ({product.review_count} reviews)</span>
          {product.in_stock
            ? <span className="ml-auto text-xs bg-green-50 text-green-700 border border-green-200 rounded-full px-2 py-0.5 whitespace-nowrap">✓ In Stock</span>
            : <span className="ml-auto text-xs bg-red-50 text-red-600 rounded-full px-2 py-0.5">Out of Stock</span>
          }
        </div>

        {/* Price section */}
        <div className="flex items-baseline gap-3 mb-1">
          <span className="text-3xl font-bold text-gray-900">${product.price.toLocaleString()}</span>
          {product.price_original > product.price && (
            <span className="text-gray-400 line-through text-lg">${product.price_original.toLocaleString()}</span>
          )}
        </div>
        {savings > 0 && (
          <div className="inline-flex items-center gap-2 bg-red-50 border border-red-100 rounded-xl px-3 py-1.5 mb-3">
            <span className="text-red-600 font-bold text-sm">You save ${savings.toLocaleString()}!</span>
            {product.discount_pct > 0 && (
              <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                {product.discount_pct}% OFF
              </span>
            )}
          </div>
        )}
      </div>

      {/* Trust badges */}
      <div className="flex items-center justify-between bg-gray-50 rounded-2xl px-4 py-3 mb-5 border border-gray-100">
        <div className="flex flex-col items-center gap-1">
          <span className="text-lg">🚚</span>
          <span className="text-xs text-gray-600 font-medium text-center">Free Delivery</span>
        </div>
        <div className="w-px h-8 bg-gray-200" />
        <div className="flex flex-col items-center gap-1">
          <span className="text-lg">↩</span>
          <span className="text-xs text-gray-600 font-medium text-center">30-Day Returns</span>
        </div>
        <div className="w-px h-8 bg-gray-200" />
        <div className="flex flex-col items-center gap-1">
          <span className="text-lg">🛡</span>
          <span className="text-xs text-gray-600 font-medium text-center">10-Yr Warranty</span>
        </div>
      </div>

      {/* Add to cart section */}
      {product.in_stock && onAddToCart && (
        <div className="flex items-center gap-3 mb-5">
          <div className="flex items-center gap-2 border-2 border-gray-200 rounded-xl px-3 py-2">
            <button onClick={() => setQty(q => Math.max(1, q - 1))}
              className="w-7 h-7 rounded-full bg-gray-100 text-base flex items-center justify-center hover:bg-gray-200 transition font-bold">−</button>
            <span className="text-sm font-bold w-6 text-center">{qty}</span>
            <button onClick={() => setQty(q => q + 1)}
              className="w-7 h-7 rounded-full bg-gray-100 text-base flex items-center justify-center hover:bg-gray-200 transition font-bold">+</button>
          </div>
          <button
            onClick={handleAdd}
            className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all duration-200 ${
              added
                ? 'bg-green-50 text-green-600 border-2 border-green-200'
                : 'text-white hover:opacity-90 shadow-md'
            }`}
            style={added ? {} : { background: '#0D5C6E' }}
          >
            {added ? '✓ Added to Cart!' : `Add ${qty > 1 ? `${qty}× ` : ''}to Cart`}
          </button>
        </div>
      )}

      {product.pdf_url && (
        <a href={product.pdf_url} target="_blank" rel="noreferrer"
           className="inline-flex items-center gap-1.5 text-xs font-medium border rounded-lg px-3 py-1.5 transition-colors mb-5 self-start"
           style={{ color: '#0D5C6E', borderColor: '#0D5C6E' }}
           onMouseOver={e => { e.currentTarget.style.background='#0D5C6E'; e.currentTarget.style.color='white' }}
           onMouseOut={e => { e.currentTarget.style.background=''; e.currentTarget.style.color='#0D5C6E' }}>
          📄 Download Spec Sheet (PDF)
        </a>
      )}

      {/* Key Highlights */}
      {product.highlights?.length > 0 && (
        <div className="mb-5">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="font-bold text-gray-800 text-base">Key Highlights</h3>
            <div className="flex-1 h-px bg-gray-200" />
          </div>
          <div className="grid grid-cols-2 gap-2">
            {product.highlights.map((h, i) => (
              <div key={i} className="flex items-start gap-2 rounded-xl p-3 text-sm text-gray-700 border border-gray-100 bg-white shadow-sm">
                <span className="font-bold mt-0.5 flex-shrink-0" style={{ color: '#0D5C6E' }}>✓</span>
                <span>{h}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Specifications table */}
      {product.specs && (
        <div className="mb-5">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="font-bold text-gray-800 text-base">Specifications</h3>
            <div className="flex-1 h-px bg-gray-200" />
          </div>
          <div className="rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            {Object.entries(product.specs).map(([k, v], i) => (
              <div key={k} className={`flex px-4 py-3 text-sm ${i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                <span className="w-44 text-gray-500 font-semibold flex-shrink-0">{k}</span>
                <span className="text-gray-800 font-medium">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* In the Box */}
      <div className="mb-5">
        <div className="flex items-center gap-3 mb-3">
          <h3 className="font-bold text-gray-800 text-base">In the Box</h3>
          <div className="flex-1 h-px bg-gray-200" />
        </div>
        <ul className="space-y-1.5 pl-1">
          {['1× Main Unit', '1× Power Cable', '1× User Manual', '1× Warranty Card'].map((item, i) => (
            <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
              <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: '#0D5C6E' }} />
              {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
