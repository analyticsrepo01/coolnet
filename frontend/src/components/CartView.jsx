export default function CartView({ cart, onBack, onUpdateQty, onRemove, onCheckout, agentColor, onApplyDiscount }) {
  const color = agentColor || '#0D5C6E'
  const subtotal = cart.reduce((s, item) => s + item.product.price * item.quantity, 0)
  const gst      = subtotal * 0.09
  const total    = subtotal + gst

  if (cart.length === 0) return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-4">
        <button onClick={onBack} className="text-brand text-sm hover:underline">← Catalogue</button>
        <span className="text-gray-500 font-medium text-sm">/ Cart</span>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
        <div className="text-5xl mb-3">🛒</div>
        <p className="text-sm">Your cart is empty</p>
        <button onClick={onBack} className="mt-4 text-sm text-brand hover:underline">Browse products</button>
      </div>
    </div>
  )

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <button onClick={onBack} className="text-brand text-sm hover:underline flex-shrink-0">← Catalogue</button>
        <span className="text-gray-500 font-medium text-sm">
          / Cart ({cart.reduce((s, i) => s + i.quantity, 0)} items)
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 min-h-0">
        {cart.map(({ product, quantity, discountedFrom }) => (
          <div key={product.sku} className="bg-white rounded-2xl p-3 shadow-sm border border-gray-100 flex gap-3">
            <div className="w-16 h-16 flex-shrink-0 rounded-xl overflow-hidden bg-gray-50 flex items-center justify-center">
              {product.image
                ? <img src={product.image} alt={product.name} className="w-full h-full object-contain p-1"
                       onError={e => { e.target.style.display='none' }} />
                : <span className="text-2xl">{product.emoji || '📦'}</span>}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-gray-800 leading-tight line-clamp-2">{product.name}</p>
              <p className="text-xs text-gray-400 mt-0.5">{product.brand}</p>
              <div className="flex items-center justify-between mt-2">
                <div>
                  <span className="text-sm font-bold" style={{ color }}>
                    S${(product.price * quantity).toLocaleString('en-SG', { minimumFractionDigits: 2 })}
                  </span>
                  {discountedFrom && (
                    <span className="text-xs text-gray-400 line-through ml-1.5">
                      S${(discountedFrom * quantity).toLocaleString('en-SG', { minimumFractionDigits: 2 })}
                    </span>
                  )}
                  {discountedFrom && (
                    <span className="ml-1.5 text-xs font-medium text-green-600 bg-green-50 px-1.5 py-0.5 rounded-full">
                      Loyalty discount
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1.5 ml-2">
                  <button
                    onClick={() => onUpdateQty(product.sku, -1)}
                    className="w-6 h-6 rounded-full border border-gray-200 text-sm flex items-center justify-center hover:bg-gray-50 transition"
                  >−</button>
                  <span className="text-xs font-medium w-5 text-center">{quantity}</span>
                  <button
                    onClick={() => onUpdateQty(product.sku, 1)}
                    className="w-6 h-6 rounded-full border border-gray-200 text-sm flex items-center justify-center hover:bg-gray-50 transition"
                  >+</button>
                </div>
              </div>
            </div>
            <button
              onClick={() => onRemove(product.sku)}
              className="text-gray-300 hover:text-red-400 text-sm self-start mt-0.5 transition flex-shrink-0"
            >✕</button>
          </div>
        ))}
      </div>

      <div className="pt-4 mt-3 border-t border-gray-100 space-y-2">
        <div className="flex justify-between text-sm text-gray-500">
          <span>Subtotal</span>
          <span>S${subtotal.toLocaleString('en-SG', { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="flex justify-between text-sm text-gray-500">
          <span>GST (9%)</span>
          <span>S${gst.toLocaleString('en-SG', { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="flex justify-between text-base font-bold text-gray-800 pt-2 border-t border-gray-100">
          <span>Total</span>
          <span style={{ color }}>S${total.toLocaleString('en-SG', { minimumFractionDigits: 2 })}</span>
        </div>
        <button
          onClick={onCheckout}
          className="w-full py-3 rounded-2xl text-white font-semibold text-sm transition-all duration-200 mt-1 shadow-sm hover:opacity-90"
          style={{ background: color }}
        >
          Proceed to Checkout →
        </button>
      </div>
    </div>
  )
}
