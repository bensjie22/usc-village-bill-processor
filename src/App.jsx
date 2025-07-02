import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Upload, FileText, Download, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [billType, setBillType] = useState('electric')
  const [monthYear, setMonthYear] = useState('May 2025')

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0]
    if (uploadedFile && uploadedFile.type === 'application/pdf') {
      setFile(uploadedFile)
      setError(null)
    } else {
      setError('Please upload a PDF file')
    }
  }

  const handleDrop = (event) => {
    event.preventDefault()
    const droppedFile = event.dataTransfer.files[0]
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile)
      setError(null)
    } else {
      setError('Please upload a PDF file')
    }
  }

  const handleDragOver = (event) => {
    event.preventDefault()
  }

  const processFile = async () => {
    if (!file) return

    setProcessing(true)
    setProgress(0)
    setError(null)

    try {
      // Create form data
      const formData = new FormData()
      formData.append('file', file)
      formData.append('billType', billType)
      formData.append('monthYear', monthYear)

      // Start progress simulation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 800)

      // Make API call
      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()
      
      clearInterval(progressInterval)
      setProgress(100)

      if (data.success) {
        setResult({
          totalBills: data.total_bills,
          fileName: `USC Village ${billType} Bills - ${monthYear}.zip`,
          downloadUrl: data.download_url,
          summary: data.summary
        })
      } else {
        setError(data.error || 'Processing failed. Please try again.')
      }
      
    } catch (err) {
      setError('Network error. Please check your connection and try again.')
      console.error('Processing error:', err)
    } finally {
      setProcessing(false)
    }
  }

  const downloadFile = () => {
    if (result && result.downloadUrl) {
      window.open(result.downloadUrl, '_blank')
    }
  }

  const reset = () => {
    setFile(null)
    setProcessing(false)
    setProgress(0)
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            USC Village Bill Processor
          </h1>
          <p className="text-lg text-gray-600">
            Automatically separate batch utility bills into individual PDFs
          </p>
        </div>

        {/* Main Card */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-6 w-6" />
              Upload Utility Bills
            </CardTitle>
            <CardDescription>
              Upload your batch PDF file and we'll separate it into individual bills with proper naming
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Bill Type Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Bill Type</label>
              <div className="flex gap-4">
                <Button
                  variant={billType === 'electric' ? 'default' : 'outline'}
                  onClick={() => setBillType('electric')}
                  className="flex-1"
                  disabled={processing}
                >
                  Electric Bills
                </Button>
                <Button
                  variant={billType === 'water' ? 'default' : 'outline'}
                  onClick={() => setBillType('water')}
                  className="flex-1"
                  disabled={processing}
                >
                  Water Bills
                </Button>
              </div>
            </div>

            {/* Month/Year Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Billing Period</label>
              <input
                type="text"
                value={monthYear}
                onChange={(e) => setMonthYear(e.target.value)}
                placeholder="May 2025"
                disabled={processing}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>

            {/* File Upload Area */}
            {!file && !result && (
              <div
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => !processing && document.getElementById('file-input').click()}
              >
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-700 mb-2">
                  Drop your PDF file here or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Supports PDF files up to 50MB
                </p>
                <input
                  id="file-input"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  disabled={processing}
                  className="hidden"
                />
              </div>
            )}

            {/* File Selected */}
            {file && !processing && !result && (
              <div className="space-y-4">
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>{file.name}</strong> ready for processing
                    <br />
                    <span className="text-sm text-gray-600">
                      {(file.size / 1024 / 1024).toFixed(2)} MB • {billType} bills • {monthYear}
                    </span>
                  </AlertDescription>
                </Alert>
                
                <div className="flex gap-3">
                  <Button onClick={processFile} className="flex-1" disabled={processing}>
                    <FileText className="h-4 w-4 mr-2" />
                    Process Bills
                  </Button>
                  <Button variant="outline" onClick={reset} disabled={processing}>
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {/* Processing */}
            {processing && (
              <div className="space-y-4">
                <Alert>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <AlertDescription>
                    Processing your {billType} bills for {monthYear}...
                  </AlertDescription>
                </Alert>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} className="w-full" />
                </div>
                
                <div className="text-sm text-gray-600 space-y-1">
                  {progress < 30 && <p>📄 Analyzing PDF structure...</p>}
                  {progress >= 30 && progress < 60 && <p>🔍 Extracting bill information...</p>}
                  {progress >= 60 && progress < 90 && <p>✂️ Separating individual bills...</p>}
                  {progress >= 90 && <p>📦 Creating download package...</p>}
                </div>
              </div>
            )}

            {/* Results */}
            {result && (
              <div className="space-y-4">
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    <strong>Success!</strong> {result.summary}
                  </AlertDescription>
                </Alert>

                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Download Package</span>
                    <Badge variant="secondary">{result.totalBills} bills</Badge>
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    <p>📁 {result.fileName}</p>
                    <p>📋 Includes summary report</p>
                    <p>🏷️ Proper naming convention applied</p>
                  </div>
                  
                  <Button onClick={downloadFile} className="w-full" size="lg">
                    <Download className="h-4 w-4 mr-2" />
                    Download Separated Bills
                  </Button>
                </div>

                <Button variant="outline" onClick={reset} className="w-full">
                  Process Another File
                </Button>
              </div>
            )}

            {/* Error */}
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Info Cards */}
        <div className="grid md:grid-cols-2 gap-6 mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">How It Works</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>• Upload your batch PDF with multiple bills</p>
              <p>• Select bill type (Electric or Water)</p>
              <p>• Enter the billing period</p>
              <p>• Download individual PDFs with proper naming</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Naming Convention</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p className="font-mono text-xs bg-gray-100 p-2 rounded">
                USC Village - [Suite#]-[Tenant] [Type] - [Month Year].pdf
              </p>
              <p>Example:</p>
              <p className="font-mono text-xs bg-gray-100 p-2 rounded">
                USC Village - 344A-Amazon Electric - May 2025.pdf
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>Built for USC Village property management • Secure processing • No data stored</p>
        </div>
      </div>
    </div>
  )
}

export default App

