import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Select,
  DatePicker,
  Space,
  Typography,
  Spin,
  Alert,
  Tag,
  Tooltip,
  Button,
  Divider
} from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import {
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  StopOutlined,
  ReloadOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';
import { useETLStore } from '../store/etlStore';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface DashboardData {
  kpis: {
    totalCustomers: number;
    totalRevenue: number;
    totalOrders: number;
    totalReturns: number;
    customerGrowth: number;
    revenueGrowth: number;
    orderGrowth: number;
    returnGrowth: number;
  };
  statusBreakdown: {
    name: string;
    value: number;
    color: string;
    percentage: number;
  }[];
  bomAnalysis: {
    totalParts: number;
    activeParts: number;
    inactiveParts: number;
    pendingParts: number;
    categoryBreakdown: {
      category: string;
      count: number;
      percentage: number;
    }[];
  };
  timeSeriesData: {
    date: string;
    orders: number;
    revenue: number;
    customers: number;
  }[];
  topProducts: {
    partNumber: string;
    description: string;
    quantity: number;
    revenue: number;
    status: string;
  }[];
}

export const Dashboard: React.FC = () => {
  const { isDark } = useTheme();
  const { sessionData } = useETLStore();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Color palette for charts
  const colors = {
    primary: isDark ? '#1890ff' : '#722ed1',
    success: '#52c41a',
    warning: '#faad14',
    error: '#ff4d4f',
    info: '#13c2c2',
    purple: '#722ed1',
    blue: '#1890ff',
    cyan: '#13c2c2',
    green: '#52c41a',
    orange: '#fa8c16'
  };

  const statusColors = [colors.success, colors.warning, colors.error, colors.info];

  useEffect(() => {
    if (sessionData.uploadedFile) {
      generateDashboardData();
    }
  }, [sessionData.uploadedFile, selectedTimeRange, selectedCategory]);

  const generateDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch real data from backend
      const response = await fetch('http://localhost:8000/dashboard/data');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const backendData = await response.json();

      // Transform backend data to match frontend interface
      const transformedData: DashboardData = {
        kpis: {
          totalCustomers: backendData.kpis.total_customers,
          totalRevenue: backendData.kpis.total_revenue,
          totalOrders: backendData.kpis.total_orders,
          totalReturns: backendData.kpis.total_returns,
          customerGrowth: backendData.kpis.customer_growth,
          revenueGrowth: backendData.kpis.revenue_growth,
          orderGrowth: backendData.kpis.order_growth,
          returnGrowth: backendData.kpis.return_growth
        },
        statusBreakdown: backendData.status_breakdown.map((item: any) => ({
          name: item.name,
          value: item.value,
          color: item.color,
          percentage: item.percentage
        })),
        bomAnalysis: {
          totalParts: backendData.bom_analysis.total_parts || 0,
          activeParts: backendData.bom_analysis.active_parts || 0,
          inactiveParts: backendData.bom_analysis.inactive_parts || 0,
          pendingParts: backendData.bom_analysis.pending_parts || 0,
          categoryBreakdown: backendData.bom_analysis.category_breakdown || []
        },
        timeSeriesData: backendData.time_series_data.map((item: any) => ({
          date: item.date,
          orders: item.orders,
          revenue: item.revenue,
          customers: item.customers
        })),
        topProducts: backendData.top_products.map((item: any) => ({
          partNumber: item.part_number,
          description: item.description,
          quantity: item.quantity,
          revenue: item.revenue,
          status: item.status
        }))
      };

      setDashboardData(transformedData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Fallback to mock data if backend fails
      const mockData: DashboardData = {
        kpis: {
          totalCustomers: 567899,
          totalRevenue: 3465000,
          totalOrders: 1136,
          totalReturns: 1789,
          customerGrowth: 2.5,
          revenueGrowth: 5.8,
          orderGrowth: -0.2,
          returnGrowth: 0.12
        },
        statusBreakdown: [
          { name: 'Active (D)', value: 45, color: colors.success, percentage: 45 },
          { name: 'Check (0)', value: 30, color: colors.warning, percentage: 30 },
          { name: 'Inactive (X)', value: 20, color: colors.error, percentage: 20 },
          { name: 'Not Found', value: 5, color: colors.info, percentage: 5 }
        ],
        bomAnalysis: {
          totalParts: 2847,
          activeParts: 1281,
          inactiveParts: 569,
          pendingParts: 854,
          categoryBreakdown: [
            { category: 'Electronics', count: 1200, percentage: 42 },
            { category: 'Mechanical', count: 800, percentage: 28 },
            { category: 'Hardware', count: 500, percentage: 18 },
            { category: 'Software', count: 347, percentage: 12 }
          ]
        },
        timeSeriesData: generateTimeSeriesData(),
        topProducts: generateTopProducts()
      };
      setDashboardData(mockData);
    } finally {
      setLoading(false);
    }
  };

  const generateTimeSeriesData = () => {
    const data = [];
    const now = new Date();
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toISOString().split('T')[0],
        orders: Math.floor(Math.random() * 100) + 50,
        revenue: Math.floor(Math.random() * 50000) + 25000,
        customers: Math.floor(Math.random() * 200) + 100
      });
    }
    return data;
  };

  const generateTopProducts = () => {
    const statuses = ['Active', 'Pending', 'Inactive'];
    return Array.from({ length: 10 }, (_, i) => ({
      partNumber: `YZK-${String(i + 1).padStart(4, '0')}`,
      description: `Component ${i + 1}`,
      quantity: Math.floor(Math.random() * 1000) + 100,
      revenue: Math.floor(Math.random() * 100000) + 10000,
      status: statuses[Math.floor(Math.random() * statuses.length)]
    }));
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  const getGrowthIcon = (growth: number) => {
    if (growth > 0) return <RiseOutlined style={{ color: colors.success }} />;
    if (growth < 0) return <FallOutlined style={{ color: colors.error }} />;
    return <span style={{ color: colors.warning }}>—</span>;
  };

  const renderKPICards = () => {
    if (!dashboardData) return null;

    const kpiData = [
      {
        title: 'Total Customers',
        value: dashboardData.kpis.totalCustomers,
        growth: dashboardData.kpis.customerGrowth,
        icon: <TrophyOutlined />,
        color: colors.blue
      },
      {
        title: 'Total Revenue',
        value: formatCurrency(dashboardData.kpis.totalRevenue),
        growth: dashboardData.kpis.revenueGrowth,
        icon: <RiseOutlined />,
        color: colors.green
      },
      {
        title: 'Total Orders',
        value: formatNumber(dashboardData.kpis.totalOrders),
        growth: dashboardData.kpis.orderGrowth,
        icon: <FileTextOutlined />,
        color: colors.purple
      },
      {
        title: 'Total Returns',
        value: formatNumber(dashboardData.kpis.totalReturns),
        growth: dashboardData.kpis.returnGrowth,
        icon: <ExclamationCircleOutlined />,
        color: colors.orange
      }
    ];

    return (
      <Row gutter={[16, 16]} className="mb-6">
        {kpiData.map((kpi, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card
              className={`transition-all duration-300 hover:shadow-lg ${
                isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <Text className={isDark ? 'text-vista-700' : 'text-gray-600'}>
                    {kpi.title}
                  </Text>
                  <div className="flex items-center mt-1">
                    <Statistic
                      value={kpi.value}
                      valueStyle={{ 
                        fontSize: '24px', 
                        fontWeight: 'bold',
                        color: isDark ? '#1f2937' : '#374151'
                      }}
                    />
                    <div className="ml-2 flex items-center">
                      {getGrowthIcon(kpi.growth)}
                      <Text 
                        className={`ml-1 ${
                          kpi.growth > 0 ? 'text-green-500' : 
                          kpi.growth < 0 ? 'text-red-500' : 'text-yellow-500'
                        }`}
                      >
                        {Math.abs(kpi.growth)}%
                      </Text>
                    </div>
                  </div>
                </div>
                <div 
                  className="text-3xl p-3 rounded-lg"
                  style={{ backgroundColor: `${kpi.color}20`, color: kpi.color }}
                >
                  {kpi.icon}
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" />
        <Text className="ml-4">Processing dashboard data...</Text>
      </div>
    );
  }

  if (!sessionData.uploadedFile) {
    return (
      <Alert
        message="No Data Available"
        description="Please upload a file with MasterBOM and Status sheets to view the dashboard."
        type="info"
        showIcon
        className="m-4"
      />
    );
  }

  return (
    <div className={`p-6 ${isDark ? 'bg-vista-25' : 'bg-gray-50'} min-h-screen`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <Title level={2} className={isDark ? 'text-vista-900' : 'text-gray-900'}>
            📊 Analytics Dashboard
          </Title>
          <Text className={isDark ? 'text-vista-600' : 'text-gray-600'}>
            Comprehensive insights from your MasterBOM and Status data
          </Text>
        </div>
        <Space>
          <Select
            value={selectedTimeRange}
            onChange={setSelectedTimeRange}
            style={{ width: 120 }}
          >
            <Option value="7d">Last 7 days</Option>
            <Option value="30d">Last 30 days</Option>
            <Option value="90d">Last 90 days</Option>
            <Option value="1y">Last year</Option>
          </Select>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={generateDashboardData}
            loading={loading}
          >
            Refresh
          </Button>
          <Button 
            type="primary" 
            icon={<DownloadOutlined />}
          >
            Export
          </Button>
        </Space>
      </div>

      {/* KPI Cards */}
      {renderKPICards()}

      {/* Main Charts Row */}
      <Row gutter={[16, 16]} className="mb-6">
        {/* Status Breakdown Pie Chart */}
        <Col xs={24} lg={12}>
          <Card
            title="📈 Status Distribution"
            className={`h-96 ${isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}`}
          >
            {dashboardData && (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={dashboardData.statusBreakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {dashboardData.statusBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>

        {/* Time Series Chart */}
        <Col xs={24} lg={12}>
          <Card
            title="📊 Performance Trends"
            className={`h-96 ${isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}`}
          >
            {dashboardData && (
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={dashboardData.timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="orders"
                    stackId="1"
                    stroke={colors.blue}
                    fill={colors.blue}
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="customers"
                    stackId="1"
                    stroke={colors.green}
                    fill={colors.green}
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>
      </Row>

      {/* BOM Analysis Summary */}
      {dashboardData && dashboardData.bomAnalysis && (
        <Row gutter={[16, 16]} className="mb-6">
          <Col xs={24} lg={16}>
            <Card
              title="🔧 BOM Category Analysis"
              className={`h-96 ${isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}`}
            >
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={dashboardData.bomAnalysis.categoryBreakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="count" fill={colors.primary} name="Part Count" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col xs={24} lg={8}>
            <Card
              title="📊 BOM Summary"
              className={`h-96 ${isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}`}
            >
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Text>Total Parts</Text>
                  <Text strong>{formatNumber(dashboardData.bomAnalysis.totalParts)}</Text>
                </div>
                <Divider className="my-2" />
                <div className="flex justify-between items-center">
                  <Text>Active Parts</Text>
                  <Text strong style={{ color: colors.success }}>
                    {formatNumber(dashboardData.bomAnalysis.activeParts)}
                  </Text>
                </div>
                <div className="flex justify-between items-center">
                  <Text>Pending Parts</Text>
                  <Text strong style={{ color: colors.warning }}>
                    {formatNumber(dashboardData.bomAnalysis.pendingParts)}
                  </Text>
                </div>
                <div className="flex justify-between items-center">
                  <Text>Inactive Parts</Text>
                  <Text strong style={{ color: colors.error }}>
                    {formatNumber(dashboardData.bomAnalysis.inactiveParts)}
                  </Text>
                </div>
                <Divider className="my-2" />
                <div className="text-center">
                  <Progress
                    type="circle"
                    percent={Math.round((dashboardData.bomAnalysis.activeParts / dashboardData.bomAnalysis.totalParts) * 100)}
                    strokeColor={colors.success}
                    format={(percent) => `${percent}% Active`}
                  />
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* Top Products Table */}
      {dashboardData && dashboardData.topProducts && (
        <Row gutter={[16, 16]}>
          <Col xs={24}>
            <Card
              title="🏆 Top Products"
              className={isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}
            >
              <Table
                dataSource={dashboardData.topProducts}
                rowKey="partNumber"
                pagination={false}
                size="small"
                columns={[
                  {
                    title: 'Part Number',
                    dataIndex: 'partNumber',
                    key: 'partNumber',
                    render: (text: string) => <Text strong>{text}</Text>
                  },
                  {
                    title: 'Description',
                    dataIndex: 'description',
                    key: 'description'
                  },
                  {
                    title: 'Quantity',
                    dataIndex: 'quantity',
                    key: 'quantity',
                    render: (qty: number) => formatNumber(qty)
                  },
                  {
                    title: 'Revenue',
                    dataIndex: 'revenue',
                    key: 'revenue',
                    render: (revenue: number) => formatCurrency(revenue)
                  },
                  {
                    title: 'Status',
                    dataIndex: 'status',
                    key: 'status',
                    render: (status: string) => (
                      <Tag color={
                        status === 'Active' ? 'green' :
                        status === 'Pending' ? 'orange' : 'red'
                      }>
                        {status}
                      </Tag>
                    )
                  }
                ]}
              />
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};
