import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UploadCloud,
  Image as ImageIcon,
  FileText,
  History,
  Settings,
  HelpCircle,
} from 'lucide-react';

export const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Upload', path: '/upload', icon: UploadCloud },
    { name: 'Image Analysis', path: '/image-analysis', icon: ImageIcon },
    { name: 'Document Analysis', path: '/document-analysis', icon: FileText },
    { name: 'History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'About & Help', path: '/about', icon: HelpCircle },
  ];

  return (
    <aside
      className="w-64 bg-white border-r border-slate-200 hidden md:flex flex-col shrink-0 min-h-[calc(100vh-4rem)] p-4"
      aria-label="Workspace Navigation"
    >
      <div className="space-y-1.5 flex-1">
        <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Main Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-200'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`}
                    aria-hidden="true"
                  />
                  <span>{item.name}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Accessibility Quick Status */}
      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl mt-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" aria-hidden="true" />
          <span>Screen Reader Ready</span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          High-contrast & audio narration support active.
        </p>
      </div>
    </aside>
  );
};
export default Sidebar;

