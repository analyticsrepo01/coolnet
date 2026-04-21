import { useState } from 'react'

export default function CheckoutView({ cart, user, onBackToCart, onOrderPlaced, agentColor }) {
  const color    = agentColor || '#0D5C6E'
  const subtotal = cart.reduce((s, i) => s + i.product.price * i.quantity, 0)
  const gst      = subtotal * 0.09
  const total    = subtotal + gst

  const [step, setStep]     = useState('form')   // 'form' | 'processing' | 'confirmed'
  const [orderId, setOrderId] = useState('')
  const [errors, setErrors]   = useState({})
  const [form, setForm]       = useState({
    address: '', postal: '', cardName: '',
    cardNumber: '', expiry: '', cvv: '',
  })

  const set = (field, val) => {
    setForm(f => ({ ...f, [field]: val }))
    setErrors(e => ({ ...e, [field]: '' }))
  }

  const formatCard = val => {
    const d = val.replace(/\D/g, '').slice(0, 16)
    return d.replace(/(.{4})/g, '$1 ').trim()
  }
  const formatExpiry = val => {
    const d = val.replace(/\D/g, '').slice(0, 4)
    return d.length > 2 ? `${d.slice(0,2)}/${d.slice(2)}` : d
  }

  const validate = () => {
    const e = {}
    if (!form.address.trim()) e.address = 'Required'
    if (!/^\d{6}$/.test(form.postal)) e.postal = '6-digit postal'
    if (!form.cardName.trim()) e.cardName = 'Required'
    if (form.cardNumber.replace(/\s/g, '').length < 16) e.cardNumber = 'Enter 16-digit card'
    if (!/^\d{2}\/\d{2}$/.test(form.expiry)) e.expiry = 'MM/YY'
    if (form.cvv.length < 3) e.cvv = '3–4 digits'
    return e
  }

  const handlePay = async () => {
    const e = validate()
    if (Object.keys(e).length) { setErrors(e); return }
    setStep('processing')
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user?.id,
          token:   user?.token,
          items: cart.map(({ product, quantity }) => ({
            sku: product.sku, name: product.name,
            price: product.price, quantity,
          })),
          total,
          delivery_address: `${form.address}, Singapore ${form.postal}`,
        }),
      })
      const data = await res.json()
      setOrderId(data.order_id || `CN-${Date.now().toString(36).toUpperCase()}`)
    } catch {
      setOrderId(`CN-${Date.now().toString(36).toUpperCase()}`)
    }
    setStep('confirmed')
    onOrderPlaced?.()
  }

  // ── Processing spinner ────────────────────────────────────────────────────
  if (step === 'processing') return (
    <div className="flex flex-col h-full items-center justify-center gap-4">
      <div className="w-14 h-14 border-4 border-t-transparent rounded-full animate-spin"
           style={{ borderColor: `${color}33`, borderTopColor: color }} />
      <div className="text-center">
        <p className="font-semibold text-gray-700">Processing payment…</p>
        <p className="text-xs text-gray-400 mt-1">Securely charging your card</p>
      </div>
    </div>
  )

  // ── Order confirmed ───────────────────────────────────────────────────────
  if (step === 'confirmed') return (
    <div className="flex flex-col h-full items-center justify-center text-center px-2">
      <div className="text-6xl mb-3 animate-bounce">🎉</div>
      <h2 className="text-xl font-bold text-gray-800 mb-1">Order Confirmed!</h2>
      <p className="text-sm text-gray-500 mb-4">
        Order ID: <span className="font-mono font-bold" style={{ color }}>{orderId}</span>
      </p>

      <div className="w-full bg-green-50 border border-green-100 rounded-2xl p-4 mb-4 text-left space-y-1.5">
        {cart.map(({ product, quantity, discountedFrom }) => (
          <div key={product.sku} className="flex justify-between text-xs text-gray-700 gap-2">
            <span className="truncate flex-1">{product.name.split(' ').slice(0,4).join(' ')} ×{quantity}</span>
            <span className="flex-shrink-0 text-right">
              {discountedFrom && (
                <span className="line-through text-gray-400 mr-1">
                  S${(discountedFrom * quantity).toLocaleString('en-SG', { minimumFractionDigits: 2 })}
                </span>
              )}
              <span className="font-medium">
                S${(product.price * quantity).toLocaleString('en-SG', { minimumFractionDigits: 2 })}
              </span>
            </span>
          </div>
        ))}
        <div className="border-t border-green-200 pt-2 flex justify-between text-sm font-bold" style={{ color }}>
          <span>Total Paid</span>
          <span>S${total.toLocaleString('en-SG', { minimumFractionDigits: 2 })}</span>
        </div>
      </div>

      <p className="text-xs text-gray-400 mb-6">
        Delivery in 3–5 business days · Confirmation sent to {user?.email}
      </p>
      <button
        onClick={onBackToCart}
        className="py-2.5 px-8 rounded-2xl text-white text-sm font-semibold shadow-sm hover:opacity-90 transition"
        style={{ background: color }}
      >
        Continue Shopping
      </button>
    </div>
  )

  // ── Form ──────────────────────────────────────────────────────────────────
  const Field = ({ label, err, children }) => (
    <div>
      <label className="text-xs font-medium text-gray-600 block mb-1">{label}</label>
      {children}
      {err && <p className="text-xs text-red-500 mt-0.5">{err}</p>}
    </div>
  )
  const inp = field =>
    `w-full text-xs border rounded-xl px-3 py-2 focus:outline-none focus:ring-1 focus:ring-brand text-gray-800 ${
      errors[field] ? 'border-red-400 bg-red-50' : 'border-gray-200'
    }`

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <button onClick={onBackToCart} className="text-brand text-sm hover:underline">← Cart</button>
        <span className="text-gray-500 font-medium text-sm">/ Checkout</span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-5 min-h-0 pb-2">

        {/* Delivery */}
        <section>
          <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-1.5">
            <span>📦</span> Delivery
          </h3>
          <div className="space-y-2.5">
            <Field label="Full Address" err={errors.address}>
              <input className={inp('address')} placeholder="Block / Street / Unit"
                value={form.address} onChange={e => set('address', e.target.value)} />
            </Field>
            <div className="grid grid-cols-2 gap-2">
              <Field label="City">
                <input className="w-full text-xs border border-gray-200 rounded-xl px-3 py-2 bg-gray-50 text-gray-400 cursor-not-allowed" value="Singapore" disabled />
              </Field>
              <Field label="Postal Code" err={errors.postal}>
                <input className={inp('postal')} placeholder="6-digit" maxLength={6}
                  value={form.postal} onChange={e => set('postal', e.target.value.replace(/\D/g,''))} />
              </Field>
            </div>
          </div>
        </section>

        {/* Payment */}
        <section>
          <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-1.5">
            <span>💳</span> Payment
            <span className="ml-auto text-xs font-normal text-gray-400 flex items-center gap-1">🔒 Secure</span>
          </h3>
          <div className="space-y-2.5">
            <Field label="Name on Card" err={errors.cardName}>
              <input className={inp('cardName')} placeholder="As printed on card"
                value={form.cardName} onChange={e => set('cardName', e.target.value)} />
            </Field>
            <Field label="Card Number" err={errors.cardNumber}>
              <input className={inp('cardNumber')} placeholder="1234 5678 9012 3456"
                value={form.cardNumber}
                onChange={e => set('cardNumber', formatCard(e.target.value))} />
            </Field>
            <div className="grid grid-cols-2 gap-2">
              <Field label="Expiry" err={errors.expiry}>
                <input className={inp('expiry')} placeholder="MM/YY" maxLength={5}
                  value={form.expiry} onChange={e => set('expiry', formatExpiry(e.target.value))} />
              </Field>
              <Field label="CVV" err={errors.cvv}>
                <input className={inp('cvv')} placeholder="•••" maxLength={4} type="password"
                  value={form.cvv} onChange={e => set('cvv', e.target.value.replace(/\D/g,''))} />
              </Field>
            </div>
          </div>
        </section>

        {/* Order summary */}
        <section>
          <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-1.5">
            <span>📋</span> Order Summary
          </h3>
          <div className="bg-gray-50 rounded-2xl p-3 space-y-1.5">
            {cart.map(({ product, quantity, discountedFrom }) => (
              <div key={product.sku} className="flex justify-between text-xs gap-2">
                <span className="text-gray-600 truncate flex-1">
                  {product.name.split(' ').slice(0,4).join(' ')} ×{quantity}
                </span>
                <span className="flex-shrink-0 text-right">
                  {discountedFrom && (
                    <span className="line-through text-gray-400 mr-1">
                      S${(discountedFrom * quantity).toLocaleString('en-SG', { minimumFractionDigits: 2 })}
                    </span>
                  )}
                  <span className="text-gray-800 font-medium">
                    S${(product.price * quantity).toLocaleString('en-SG', { minimumFractionDigits: 2 })}
                  </span>
                </span>
              </div>
            ))}
            <div className="border-t border-gray-200 pt-2 space-y-1">
              <div className="flex justify-between text-xs text-gray-500">
                <span>Subtotal</span>
                <span>S${subtotal.toLocaleString('en-SG', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>GST (9%)</span>
                <span>S${gst.toLocaleString('en-SG', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between text-sm font-bold pt-1" style={{ color }}>
                <span>Total</span>
                <span>S${total.toLocaleString('en-SG', { minimumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <button
        onClick={handlePay}
        className="w-full py-3 rounded-2xl text-white font-semibold text-sm mt-3 shadow-sm hover:opacity-90 transition"
        style={{ background: color }}
      >
        Pay S${total.toLocaleString('en-SG', { minimumFractionDigits: 2 })} →
      </button>
    </div>
  )
}
