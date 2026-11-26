import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Eye, Menu, X, Home, LayoutDashboard, History, Settings, Info, Volume2 } from 'lucide-react';
import { useSettings } from '../../context/SettingsContext';

export const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { settings } = useSettings();

  const navLinks = [
    { name: 'Home', path: '/', icon: Home },
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'About', path: '/about', icon: Info },
  ];

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
      {/* Skip to Content for Screen Readers / Keyboard Navigation */}
      <a href="#main-content" className="skip-to-content">
        Skip to main content
      </a>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Brand */}
          <Link
            to="/"
            className="flex items-center gap-3 group focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-lg p-1"
            aria-label="AI Accessibility Assistant Home"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-indigo-700 flex items-center justify-center text-white shadow-md shadow-indigo-200 group-hover:scale-105 transition-transform">
              <Eye className="w-6 h-6" aria-hidden="true" />
            </div>
            <div>
              <span className="text-lg font-bold bg-gradient-to-r from-slate-900 to-indigo-900 bg-clip-text text-transparent">
                AI Accessibility
              </span>
              <span className="hidden sm:inline-block ml-1.5 px-2 py-0.5 text-xs font-semibold bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">
                Assistant
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1" aria-label="Main Navigation">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const active = isActive(link.path);
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                    active
                      ? 'bg-indigo-50 text-indigo-700 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                  aria-current={active ? 'page' : undefined}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-indigo-600' : 'text-slate-400'}`} aria-hidden="true" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right Action Button */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              <span>Upload File</span>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={isMobileMenuOpen}
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6" aria-hidden="true" />
              ) : (
                <Menu className="w-6 h-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const active = isActive(link.path);
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-base font-medium ${
                  active
                    ? 'bg-indigo-50 text-indigo-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
                aria-current={active ? 'page' : undefined}
              >
                <Icon className={`w-5 h-5 ${active ? 'text-indigo-600' : 'text-slate-400'}`} aria-hidden="true" />
                <span>{link.name}</span>
              </Link>
            );
          })}
          <div className="pt-2">
            <Link
              to="/upload"
              onClick={() => setIsMobileMenuOpen(false)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 text-white font-medium text-base shadow-sm"
            >
              Upload File
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
export default Navbar;

