import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Eye, EyeOff, GraduationCap, ShieldCheck, Building2, School, BookOpen, Compass } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

const DEMO_ACCOUNTS = [
  {
    role: 'Student',
    email: 'student.test@example.com',
    pass: 'Student@123',
    badge: 'bg-blue-100 text-blue-700 border-blue-200',
    hover: 'hover:border-blue-400 hover:bg-blue-50/50',
    icon: GraduationCap,
  },
  {
    role: 'Admin',
    email: 'admin.test@example.com',
    pass: 'Admin@123',
    badge: 'bg-purple-100 text-purple-700 border-purple-200',
    hover: 'hover:border-purple-400 hover:bg-purple-50/50',
    icon: ShieldCheck,
  },
  {
    role: 'Company',
    email: 'industry@example.com',
    pass: 'Industry@123',
    badge: 'bg-indigo-100 text-indigo-700 border-indigo-200',
    hover: 'hover:border-indigo-400 hover:bg-indigo-50/50',
    icon: Building2,
  },
  {
    role: 'College',
    email: 'institution@example.com',
    pass: 'Institution@123',
    badge: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    hover: 'hover:border-emerald-400 hover:bg-emerald-50/50',
    icon: School,
  },
  {
    role: 'Faculty',
    email: 'faculty@example.com',
    pass: 'Faculty@123',
    badge: 'bg-amber-100 text-amber-700 border-amber-200',
    hover: 'hover:border-amber-400 hover:bg-amber-50/50',
    icon: BookOpen,
  },
  {
    role: 'Mentor',
    email: 'mentor@example.com',
    pass: 'Mentor@123',
    badge: 'bg-rose-100 text-rose-700 border-rose-200',
    hover: 'hover:border-rose-400 hover:bg-rose-50/50',
    icon: Compass,
  },
]

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      const stored = localStorage.getItem('user')
      const currentUser = stored ? JSON.parse(stored) : null
      const role = (currentUser?.role || '').toUpperCase()

      switch (role) {
        case 'ADMIN':
          navigate('/dashboard')
          break
        case 'INDUSTRY_ADMIN':
        case 'INDUSTRY_MEMBER_RECRUITER':
          navigate('/company/internships')
          break
        case 'INSTITUTION_ADMIN':
          navigate('/institution/stats')
          break
        case 'FACULTY':
          navigate('/academician/opportunities')
          break
        case 'MENTOR_TRAINER':
          navigate('/mentor/dashboard')
          break
        case 'STUDENT':
        default:
          navigate('/student/learning')
          break
      }
    } catch {
      setError('Invalid email or password.')
    } finally {
      setLoading(false)
    }
  }

  const fillCredentials = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail)
    setPassword(demoPass)
    setError('')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="card w-full max-w-lg shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-700">SkillBridge AI</h1>
          <p className="text-gray-500 mt-2">Assess. Upskill. Connect. Get Hired. Grow.</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="login-email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input id="login-email" className="input" type="email" value={email}
              onChange={e => setEmail(e.target.value)} required placeholder="student.test@example.com" />
          </div>
          <div>
            <label htmlFor="login-password" className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <div className="relative">
              <input
                id="login-password"
                className="input pr-10"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(prev => !prev)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none focus:text-blue-600 transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <Eye className="h-5 w-5" aria-hidden="true" />
                )}
              </button>
            </div>
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Don't have an account? <Link to="/register" className="text-blue-600 hover:underline">Register</Link>
        </p>
        <div className="mt-6 p-4 bg-slate-50/80 border border-slate-200 rounded-xl text-xs text-gray-600">
          <div className="flex items-center justify-between mb-3">
            <p className="font-semibold text-gray-800">Demo Accounts (Click to auto-fill):</p>
            <span className="text-[11px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium border border-blue-100">
              6 Roles
            </span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {DEMO_ACCOUNTS.map((acc) => {
              const Icon = acc.icon
              return (
                <button
                  key={acc.role}
                  type="button"
                  onClick={() => fillCredentials(acc.email, acc.pass)}
                  className={`flex items-center gap-2.5 p-2 rounded-lg bg-white border border-gray-200 ${acc.hover} transition-all text-left shadow-sm group hover:shadow cursor-pointer`}
                  title={`Auto-fill ${acc.role} credentials`}
                >
                  <div className={`p-1.5 rounded-md border ${acc.badge} shrink-0`}>
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-gray-900 leading-tight">{acc.role}</span>
                      <span className="text-[10px] text-blue-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                        Fill
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-500 truncate leading-tight mt-0.5">{acc.email}</p>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
