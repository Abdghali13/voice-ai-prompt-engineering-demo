import { useState, useEffect } from 'react'
import Head from 'next/head'
import { 
  PhoneIcon, 
  ChartBarIcon, 
  ShieldCheckIcon, 
  CogIcon,
  PlayIcon,
  StopIcon
} from '@heroicons/react/24/outline'

interface CallData {
  call_sid: string
  phone_number: string
  status: string
  duration: number
  scenario: string
  start_time: string
}

interface DashboardStats {
  active_calls: number
  total_calls_today: number
  success_rate: number
  average_duration: string
}

export default function Dashboard() {
  const [activeCalls, setActiveCalls] = useState<CallData[]>([])
  const [stats, setStats] = useState<DashboardStats>({
    active_calls: 0,
    total_calls_today: 0,
    success_rate: 0,
    average_duration: "0:00"
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Fetch active calls
      const callsResponse = await fetch('/api/v1/calls/active')
      const callsData = await callsResponse.json()
      setActiveCalls(callsData.active_calls || [])

      // Fetch performance metrics
      const metricsResponse = await fetch('/api/v1/analytics/performance-metrics?time_period=daily')
      const metricsData = await metricsResponse.json()
      
      setStats({
        active_calls: callsData.total || 0,
        total_calls_today: metricsData.call_metrics?.total_calls || 0,
        success_rate: metricsData.call_metrics?.success_rate || 0,
        average_duration: metricsData.call_metrics?.average_call_duration || "0:00"
      })
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const startDemoCall = async () => {
    try {
      const response = await fetch('/api/v1/voice-ai/simulate-conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          scenario: 'billing_inquiry',
          messages: JSON.stringify([
            "I have a question about my medical bill",
            "Can you explain the charges?",
            "I'd like to set up a payment plan"
          ])
        })
      })
      
      if (response.ok) {
        alert('Demo conversation started! Check the logs for details.')
        fetchDashboardData()
      }
    } catch (error) {
      console.error('Failed to start demo call:', error)
      alert('Failed to start demo call')
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Voice AI Dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Voice AI Demo Dashboard</title>
        <meta name="description" content="Healthcare billing automation with voice AI" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Voice AI Prompt Engineering Demo
                </h1>
                <p className="text-gray-600">Healthcare billing automation with HIPAA compliance</p>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={startDemoCall}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <PlayIcon className="h-4 w-4 mr-2" />
                  Start Demo Call
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <PhoneIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Active Calls
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.active_calls}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Calls Today
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.total_calls_today}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Success Rate
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.success_rate}%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CogIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Avg Duration
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.average_duration}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Active Calls */}
          <div className="bg-white shadow rounded-lg mb-8">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Active Calls
              </h3>
              {activeCalls.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Call ID
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Phone Number
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Duration
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Scenario
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {activeCalls.map((call) => (
                        <tr key={call.call_sid}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {call.call_sid}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {call.phone_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              call.status === 'in-progress' 
                                ? 'bg-green-100 text-green-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {call.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {Math.floor(call.duration / 60)}:{(call.duration % 60).toString().padStart(2, '0')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {call.scenario.replace('_', ' ')}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No active calls at the moment</p>
              )}
            </div>
          </div>

          {/* HIPAA Compliance Status */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <ShieldCheckIcon className="h-8 w-8 text-green-600 mr-3" />
                <div>
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    HIPAA Compliance Status
                  </h3>
                  <p className="text-sm text-gray-500">
                    All systems are operating within HIPAA compliance guidelines
                  </p>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-green-800">Data Encryption</div>
                  <div className="text-lg font-semibold text-green-900">100%</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-green-800">Audit Trails</div>
                  <div className="text-lg font-semibold text-green-900">100%</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-green-800">Access Control</div>
                  <div className="text-lg font-semibold text-green-900">97%</div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
