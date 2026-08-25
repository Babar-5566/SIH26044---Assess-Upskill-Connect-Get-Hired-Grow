import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { BookOpen, Briefcase, GraduationCap, LogOut, LayoutDashboard } from 'lucide-react'

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  const studentLinks = [
    { to: '/student/learning', icon: <BookOpen size={18} />, label: 'Learning & Development' },
    { to: '/student/internships', icon: <Briefcase size={18} />, label: 'Internships' },
    { to: '/student/internships/applications', icon: <LayoutDashboard size={18} />, label: 'My Applications' },
    { to: '/student/certifications', icon: <GraduationCap size={18} />, label: 'Certifications' },
  ]
  const companyLinks = [
    { to: '/company/internships', icon: <Briefcase size={18} />, label: 'My Postings' },
    { to: '/company/internships/new', icon: <LayoutDashboard size={18} />, label: 'Post Internship' },
    { to: '/company/opportunities/new', icon: <GraduationCap size={18} />, label: 'Post FDP / Opportunity' },
  ]
  const academicianLinks = [
    { to: '/academician/opportunities', icon: <BookOpen size={18} />, label: 'Opportunities' },
  ]
  const institutionLinks = [
    { to: '/institution/stats', icon: <LayoutDashboard size={18} />, label: 'Internship Stats' },
  ]
  const roleDashboard = { to: '/dashboard', icon: <LayoutDashboard size={18} />, label: 'Dashboard' }

  const links = [roleDashboard, ...( 
    (user?.role === 'student' || user?.role === 'STUDENT') ? studentLinks :
    (user?.role === 'company' || user?.role === 'INDUSTRY_MEMBER_RECRUITER' || user?.role === 'INDUSTRY_ADMIN') ? companyLinks :
    (user?.role === 'academician' || user?.role === 'FACULTY') ? academicianLinks :
    (user?.role === 'institution' || user?.role === 'INSTITUTION_ADMIN') ? institutionLinks : [])]

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col min-h-screen">
      <div className="p-6 border-b border-gray-100">
        <h1 className="text-xl font-bold text-blue-700">SkillBridge AI</h1>
        <p className="text-xs text-gray-500 mt-1">Phase 12 & 13</p>
      </div>
      <div className="p-4 border-b border-gray-100">
        <p className="text-sm font-medium text-gray-800">{user?.full_name}</p>
        <span className="badge bg-blue-100 text-blue-700 mt-1">{user?.role}</span>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {links.map((l) => (
          <NavLink
            key={l.to} to={l.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-50'
              }`
            }
          >
            {l.icon}{l.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-100">
        <button onClick={handleLogout}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-red-600 transition-colors w-full">
          <LogOut size={16} /> Sign out
        </button>
      </div>
    </aside>
  )
}
