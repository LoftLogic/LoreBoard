import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Editor from './pages/Editor'
import Telemetry from './pages/Telemetry'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/editor" element={<Editor />} />
        <Route path="/editor/:storyId" element={<Editor />} />
        <Route path="/telemetry" element={<Telemetry />} />
      </Routes>
    </BrowserRouter>
  )
}
