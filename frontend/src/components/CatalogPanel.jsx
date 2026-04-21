import { useState, useEffect } from 'react'
import ProductCard from './ProductCard.jsx'
import ProductDetail from './ProductDetail.jsx'
import CartView from './CartView.jsx'
import CheckoutView from './CheckoutView.jsx'

const CATEGORIES = [
  { id: 'refrigerators',    name: 'Refrigerators',   icon: '🧊' },
  { id: 'tvs',              name: 'Televisions',      icon: '📺' },
  { id: 'washing_machines', name: 'Washing Machines', icon: '🌀' },
  { id: 'air_conditioners', name: 'Air Conditioners', icon: '❄️' },
  { id: 'kitchen_hobs',     name: 'Kitchen Hobs',     icon: '🍳' },
  { id: 'vacuum_cleaners',  name: 'Vacuum Cleaners',  icon: '🤖' },
  { id: 'fans',             name: 'Fans',             icon: '💨' },
  { id: 'dryers',           name: 'Dryers',           icon: '♨️' },
  { id: 'microwaves',       name: 'Microwaves',       icon: '📡' },
  { id: 'dishwashers',      name: 'Dishwashers',      icon: '🫧' },
  { id: 'small_appliances', name: 'Small Appliances', icon: '☕' },
]

const PAGE_SIZE = 4

export default function CatalogPanel({
  catalogState, agentColor, onProductSelect,
  cart, onAddToCart, onUpdateCartQty, onRemoveFromCart, onClearCart, user,
}) {
  const [view, setView]           = useState({ type: 'home' })
  const [animating, setAnimating] = useState(false)
  const [promotion, setPromotion] = useState(null)
  const [compareProducts, setCompare] = useState([])
  const [activeSubcat, setActiveSubcat] = useState('All')

  const color     = agentColor || '#0D5C6E'
  const cartCount = cart?.reduce((s, i) => s + i.quantity, 0) || 0

  // Apply catalog actions from agent
  useEffect(() => {
    if (!catalogState) return
    const { action } = catalogState

    const transition = (fn) => {
      setAnimating(true)
      setTimeout(() => { fn(); setAnimating(false) }, 350)
    }

    if (action === 'show_home') {
      transition(() => setView({ type: 'home' }))
    } else if (action === 'show_category') {
      const products = catalogState.products || []
      transition(() => {
        setActiveSubcat(catalogState.subcategory || 'All')
        setView({ type: 'category', category: catalogState.category,
                  subcategory: catalogState.subcategory, products,
                  page: catalogState.page || 1, highlightedSku: null })
      })
    } else if (action === 'highlight') {
      setView(prev => ({ ...prev, highlightedSku: catalogState.sku }))
    } else if (action === 'show_detail') {
      transition(() => setView({ type: 'detail', product: catalogState.product }))
    } else if (action === 'show_comparison') {
      transition(() => { setView({ type: 'comparison' }); setCompare(catalogState.products || []) })
    } else if (action === 'show_promotion') {
      setPromotion({ title: catalogState.title, description: catalogState.description, discount_pct: catalogState.discount_pct })
      setTimeout(() => setPromotion(null), 8000)
    } else if (action === 'add_to_cart') {
      if (catalogState.product) onAddToCart?.(catalogState.product, catalogState.quantity || 1)
    } else if (action === 'show_cart') {
      transition(() => setView({ type: 'cart' }))
    } else if (action === 'show_checkout') {
      transition(() => setView({ type: 'checkout' }))
    }
  }, [catalogState])

  // ── Cart button (shown when cart has items and not already in cart/checkout) ─
  const showCartBadge = cartCount > 0 && view.type !== 'cart' && view.type !== 'checkout'

  // ── Home ──────────────────────────────────────────────────────────────────
  const renderHome = () => (
    <div>
      <div className="mb-5">
        <h2 className="text-lg font-bold text-gray-800">CoolNest Catalogue</h2>
        <p className="text-sm text-gray-500">Smart Appliances, Smarter Prices — tell our agent what you need!</p>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {CATEGORIES.map(cat => (
          <button key={cat.id} onClick={() => fetchAndShowCategory(cat.id)}
            className="rounded-2xl border-2 border-gray-100 hover:border-brand bg-white p-4 flex flex-col items-center gap-2 transition-all duration-200 hover:shadow-md">
            <span className="text-3xl">{cat.icon}</span>
            <span className="text-xs font-medium text-gray-600 text-center leading-tight">{cat.name}</span>
          </button>
        ))}
      </div>
    </div>
  )

  async function fetchAndShowCategory(categoryId) {
    try {
      const base = window.location.pathname.replace(/\/?$/, '')
      const res  = await fetch(`${base}/api/products?category=${categoryId}`)
      const products = await res.json()
      const cat = CATEGORIES.find(c => c.id === categoryId)
      setAnimating(true); setActiveSubcat('All')
      setTimeout(() => {
        setView({ type: 'category', category: categoryId, categoryName: cat?.name, products, page: 1, highlightedSku: null })
        setAnimating(false)
      }, 350)
    } catch { }
  }

  // ── Category grid ─────────────────────────────────────────────────────────
  const renderCategory = () => {
    const { products = [], page = 1, highlightedSku, category, categoryName } = view
    const cat      = CATEGORIES.find(c => c.id === category)
    const subcats  = ['All', ...new Set(products.map(p => p.subcategory).filter(Boolean))]
    const showTabs = subcats.length > 2

    const filtered = (() => {
      if (!activeSubcat || activeSubcat === 'All') return products
      const f = products.filter(p => p.subcategory === activeSubcat)
      return f.length > 0 ? f : products
    })()

    const totalPages  = Math.ceil(filtered.length / PAGE_SIZE)
    const safePage    = Math.min(page, totalPages || 1)
    const pageProducts = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE)

    return (
      <div className="h-full flex flex-col">
        <div className="flex items-center gap-2 mb-3">
          <button onClick={() => setView({ type: 'home' })} className="text-brand text-sm hover:underline flex-shrink-0">← Catalogue</button>
          <span className="text-gray-300">/</span>
          <span className="text-gray-700 font-medium text-sm">{cat?.icon} {categoryName || cat?.name}</span>
          <span className="ml-auto text-xs text-gray-400">{filtered.length} products</span>
        </div>

        {showTabs && (
          <div className="flex gap-2 mb-4 flex-wrap">
            {subcats.map(sc => {
              const count    = sc === 'All' ? products.length : products.filter(p => p.subcategory === sc).length
              const isActive = activeSubcat === sc
              return (
                <button key={sc}
                  onClick={() => { setActiveSubcat(sc); setView(v => ({ ...v, page: 1 })) }}
                  className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                    isActive ? 'bg-brand text-white border-brand shadow-sm' : 'bg-white text-gray-600 border-gray-200 hover:border-brand hover:text-brand'
                  }`}>
                  {sc} <span className={`ml-0.5 ${isActive ? 'opacity-75' : 'opacity-50'}`}>({count})</span>
                </button>
              )
            })}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 flex-1">
          {pageProducts.map(p => (
            <ProductCard key={p.sku} product={p} highlighted={p.sku === highlightedSku}
              onAddToCart={onAddToCart}
              onSelect={p => { setView({ type: 'detail', product: p }); onProductSelect?.(p) }} />
          ))}
          {pageProducts.length === 0 && (
            <div className="col-span-2 text-center text-gray-400 text-sm mt-8">No products in this category</div>
          )}
        </div>

        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-3 mt-4 pt-3 border-t border-gray-100">
            <button onClick={() => setView(v => ({ ...v, page: Math.max(1, v.page - 1) }))}
              disabled={safePage === 1}
              className="px-3 py-1.5 text-sm rounded-lg border disabled:opacity-40 hover:bg-gray-50 transition">← Prev</button>
            <span className="text-sm text-gray-500">Page {safePage} of {totalPages}</span>
            <button onClick={() => setView(v => ({ ...v, page: Math.min(totalPages, v.page + 1) }))}
              disabled={safePage === totalPages}
              className="px-3 py-1.5 text-sm rounded-lg border disabled:opacity-40 hover:bg-gray-50 transition">Next →</button>
          </div>
        )}
      </div>
    )
  }

  // ── Comparison ────────────────────────────────────────────────────────────
  const renderComparison = () => {
    if (!compareProducts.length) return <div className="text-gray-400 text-center mt-10">No products to compare</div>
    const specs = [...new Set(compareProducts.flatMap(p => Object.keys(p.specs || {})))]
    return (
      <div>
        <div className="flex items-center gap-2 mb-4">
          <button onClick={() => setView({ type: 'home' })} className="text-brand text-sm hover:underline">← Catalogue</button>
          <span className="text-gray-500 font-medium text-sm">/ Comparing {compareProducts.length} products</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left text-gray-500 font-medium pb-2 pr-4 w-32">Feature</th>
                {compareProducts.map(p => (
                  <th key={p.sku} className="pb-2 px-2">
                    <div className="text-4xl mb-1">{p.emoji || '📦'}</div>
                    <div className="font-semibold text-gray-800 text-xs leading-tight">{p.name}</div>
                    <div className="text-brand font-bold mt-1">${p.price}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-gray-100">
                <td className="py-2 pr-4 text-gray-500">Rating</td>
                {compareProducts.map(p => (
                  <td key={p.sku} className="py-2 px-2 text-center">
                    <span className="text-yellow-400">{'★'.repeat(Math.round(p.rating))}</span>
                    <span className="text-gray-400 text-xs ml-1">({p.review_count})</span>
                  </td>
                ))}
              </tr>
              {specs.map((spec, i) => (
                <tr key={spec} className={`border-t border-gray-100 ${i % 2 === 0 ? '' : 'bg-gray-50'}`}>
                  <td className="py-2 pr-4 text-gray-500">{spec}</td>
                  {compareProducts.map(p => (
                    <td key={p.sku} className="py-2 px-2 text-center text-gray-700 text-xs">
                      {p.specs?.[spec] ? String(p.specs[spec]) : <span className="text-gray-300">—</span>}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-cream overflow-hidden relative">
      {/* Promotion banner */}
      {promotion && (
        <div className="absolute top-0 left-0 right-0 z-20 p-4 text-white text-center shadow-lg"
             style={{ background: color }}>
          <div className="font-bold text-lg">🎉 {promotion.title}</div>
          <div className="text-sm opacity-90">{promotion.description}</div>
        </div>
      )}

      {/* Floating cart badge */}
      {showCartBadge && (
        <button
          onClick={() => setView({ type: 'cart' })}
          className="absolute top-4 right-4 z-10 flex items-center gap-1.5 text-white text-xs font-semibold px-3 py-2 rounded-full shadow-lg transition-all hover:opacity-90"
          style={{ background: color }}
        >
          🛒 <span>{cartCount} {cartCount === 1 ? 'item' : 'items'}</span>
        </button>
      )}

      {/* Main content */}
      <div className="flex-1 overflow-y-auto p-5 transition-all duration-350"
           style={{ opacity: animating ? 0 : 1, transform: animating ? 'translateX(20px)' : 'translateX(0)' }}>
        {view.type === 'home'       && renderHome()}
        {view.type === 'category'   && renderCategory()}
        {view.type === 'detail'     && (
          <ProductDetail product={view.product}
            onBack={() => setView({ type: 'home' })}
            onAddToCart={onAddToCart} />
        )}
        {view.type === 'comparison' && renderComparison()}
        {view.type === 'cart'       && (
          <CartView
            cart={cart || []}
            agentColor={color}
            onBack={() => setView({ type: 'home' })}
            onUpdateQty={onUpdateCartQty}
            onRemove={onRemoveFromCart}
            onCheckout={() => setView({ type: 'checkout' })}
          />
        )}
        {view.type === 'checkout' && (
          <CheckoutView
            cart={cart || []}
            user={user}
            agentColor={color}
            onBackToCart={() => setView({ type: 'cart' })}
            onOrderPlaced={() => {
              onClearCart?.()
              // stay on confirmation screen, user clicks "Continue Shopping" to go home
            }}
          />
        )}
      </div>
    </div>
  )
}
