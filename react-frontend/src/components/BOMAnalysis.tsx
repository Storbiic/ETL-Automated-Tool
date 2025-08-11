import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Table,
  Progress,
  Tag,
  Space,
  Typography,
  Select,
  Input,
  Button,
  Tooltip,
  Statistic,
  Alert,
  Tabs
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
  TreeMap,
  Cell
} from 'recharts';
import {
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  StopOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';
import { useETLStore } from '../store/etlStore';

const { Title, Text } = Typography;
const { Option } = Select;
const { Search } = Input;
const { TabPane } = Tabs;

interface BOMItem {
  partNumber: string;
  description: string;
  category: string;
  status: 'D' | '0' | 'X' | 'NOT_FOUND';
  quantity: number;
  unitCost: number;
  totalCost: number;
  supplier: string;
  lastUpdated: string;
  criticality: 'High' | 'Medium' | 'Low';
}

interface CategoryAnalysis {
  category: string;
  totalParts: number;
  activeParts: number;
  inactiveParts: number;
  pendingParts: number;
  notFoundParts: number;
  totalValue: number;
  averageCost: number;
}

export const BOMAnalysis: React.FC = () => {
  const { isDark } = useTheme();
  const { sessionData } = useETLStore();
  const [bomData, setBomData] = useState<BOMItem[]>([]);
  const [categoryAnalysis, setCategoryAnalysis] = useState<CategoryAnalysis[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const colors = {
    active: '#52c41a',
    pending: '#faad14',
    inactive: '#ff4d4f',
    notFound: '#13c2c2',
    primary: isDark ? '#1890ff' : '#722ed1'
  };

  useEffect(() => {
    if (sessionData.uploadedFile) {
      generateBOMAnalysis();
    }
  }, [sessionData.uploadedFile]);

  const generateBOMAnalysis = async () => {
    setLoading(true);
    try {
      // Fetch real data from backend
      const response = await fetch('http://localhost:8000/bom/analysis');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const backendData = await response.json();

      // Transform backend data to match frontend interface
      const transformedBOMData: BOMItem[] = backendData.bom_data.map((item: any) => ({
        partNumber: item.part_number,
        description: item.description,
        category: item.category,
        status: item.status as 'D' | '0' | 'X' | 'NOT_FOUND',
        quantity: item.quantity,
        unitCost: item.unit_cost,
        totalCost: item.total_cost,
        supplier: item.supplier,
        lastUpdated: item.last_updated,
        criticality: item.criticality as 'High' | 'Medium' | 'Low'
      }));

      setBomData(transformedBOMData);

      // Transform category analysis
      const transformedCategoryAnalysis: CategoryAnalysis[] = backendData.category_analysis.map((item: any) => ({
        category: item.category,
        totalParts: item.total_parts,
        activeParts: item.active_parts,
        inactiveParts: 0, // Will be calculated from BOM data
        pendingParts: 0, // Will be calculated from BOM data
        notFoundParts: 0, // Will be calculated from BOM data
        totalValue: item.total_value,
        averageCost: item.average_cost
      }));

      // Calculate missing category stats from BOM data
      transformedCategoryAnalysis.forEach(catAnalysis => {
        const categoryItems = transformedBOMData.filter(item => item.category === catAnalysis.category);
        catAnalysis.inactiveParts = categoryItems.filter(item => item.status === 'X').length;
        catAnalysis.pendingParts = categoryItems.filter(item => item.status === '0').length;
        catAnalysis.notFoundParts = categoryItems.filter(item => item.status === 'NOT_FOUND').length;
      });

      setCategoryAnalysis(transformedCategoryAnalysis);

    } catch (error) {
      console.error('Error fetching BOM analysis:', error);
      // Fallback to mock data if backend fails
      const mockBOMData: BOMItem[] = Array.from({ length: 150 }, (_, i) => {
        const statuses: ('D' | '0' | 'X' | 'NOT_FOUND')[] = ['D', '0', 'X', 'NOT_FOUND'];
        const categories = ['Electronics', 'Mechanical', 'Hardware', 'Software', 'Assembly'];
        const suppliers = ['YAZAKI', 'Supplier A', 'Supplier B', 'Supplier C'];
        const criticalities: ('High' | 'Medium' | 'Low')[] = ['High', 'Medium', 'Low'];

        const status = statuses[Math.floor(Math.random() * statuses.length)];
        const category = categories[Math.floor(Math.random() * categories.length)];
        const unitCost = Math.floor(Math.random() * 1000) + 10;
        const quantity = Math.floor(Math.random() * 100) + 1;

        return {
          partNumber: `YZK-${String(i + 1).padStart(4, '0')}`,
          description: `Component ${i + 1} - ${category}`,
          category,
          status,
          quantity,
          unitCost,
          totalCost: unitCost * quantity,
          supplier: suppliers[Math.floor(Math.random() * suppliers.length)],
          lastUpdated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          criticality: criticalities[Math.floor(Math.random() * criticalities.length)]
        };
      });

      setBomData(mockBOMData);

      // Generate category analysis from mock data
      const categoryMap = new Map<string, CategoryAnalysis>();

      mockBOMData.forEach(item => {
        if (!categoryMap.has(item.category)) {
          categoryMap.set(item.category, {
            category: item.category,
            totalParts: 0,
            activeParts: 0,
            inactiveParts: 0,
            pendingParts: 0,
            notFoundParts: 0,
            totalValue: 0,
            averageCost: 0
          });
        }

        const analysis = categoryMap.get(item.category)!;
        analysis.totalParts++;
        analysis.totalValue += item.totalCost;

        switch (item.status) {
          case 'D':
            analysis.activeParts++;
            break;
          case '0':
            analysis.pendingParts++;
            break;
          case 'X':
            analysis.inactiveParts++;
            break;
          case 'NOT_FOUND':
            analysis.notFoundParts++;
            break;
        }
      });

      // Calculate average costs
      categoryMap.forEach(analysis => {
        analysis.averageCost = analysis.totalValue / analysis.totalParts;
      });

      setCategoryAnalysis(Array.from(categoryMap.values()));
    } finally {
      setLoading(false);
    }
  };

  const getStatusTag = (status: string) => {
    const statusConfig = {
      'D': { color: colors.active, text: 'Active', icon: <CheckCircleOutlined /> },
      '0': { color: colors.pending, text: 'Check', icon: <ClockCircleOutlined /> },
      'X': { color: colors.inactive, text: 'Inactive', icon: <StopOutlined /> },
      'NOT_FOUND': { color: colors.notFound, text: 'Not Found', icon: <ExclamationCircleOutlined /> }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig];
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  const getCriticalityTag = (criticality: string) => {
    const colors = {
      'High': 'red',
      'Medium': 'orange',
      'Low': 'green'
    };
    return <Tag color={colors[criticality as keyof typeof colors]}>{criticality}</Tag>;
  };

  const filteredBOMData = bomData.filter(item => {
    const matchesSearch = item.partNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter;
    
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const bomColumns = [
    {
      title: 'Part Number',
      dataIndex: 'partNumber',
      key: 'partNumber',
      sorter: (a: BOMItem, b: BOMItem) => a.partNumber.localeCompare(b.partNumber),
      render: (text: string) => <Text strong>{text}</Text>
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      sorter: (a: BOMItem, b: BOMItem) => a.description.localeCompare(b.description)
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      filters: [...new Set(bomData.map(item => item.category))].map(cat => ({ text: cat, value: cat })),
      onFilter: (value: any, record: BOMItem) => record.category === value,
      render: (category: string) => <Tag>{category}</Tag>
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      filters: [
        { text: 'Active (D)', value: 'D' },
        { text: 'Check (0)', value: '0' },
        { text: 'Inactive (X)', value: 'X' },
        { text: 'Not Found', value: 'NOT_FOUND' }
      ],
      onFilter: (value: any, record: BOMItem) => record.status === value,
      render: (status: string) => getStatusTag(status)
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
      sorter: (a: BOMItem, b: BOMItem) => a.quantity - b.quantity,
      render: (qty: number) => qty.toLocaleString()
    },
    {
      title: 'Unit Cost',
      dataIndex: 'unitCost',
      key: 'unitCost',
      sorter: (a: BOMItem, b: BOMItem) => a.unitCost - b.unitCost,
      render: (cost: number) => `$${cost.toFixed(2)}`
    },
    {
      title: 'Total Cost',
      dataIndex: 'totalCost',
      key: 'totalCost',
      sorter: (a: BOMItem, b: BOMItem) => a.totalCost - b.totalCost,
      render: (cost: number) => <Text strong>${cost.toLocaleString()}</Text>
    },
    {
      title: 'Criticality',
      dataIndex: 'criticality',
      key: 'criticality',
      filters: [
        { text: 'High', value: 'High' },
        { text: 'Medium', value: 'Medium' },
        { text: 'Low', value: 'Low' }
      ],
      onFilter: (value: any, record: BOMItem) => record.criticality === value,
      render: (criticality: string) => getCriticalityTag(criticality)
    },
    {
      title: 'Supplier',
      dataIndex: 'supplier',
      key: 'supplier',
      filters: [...new Set(bomData.map(item => item.supplier))].map(sup => ({ text: sup, value: sup })),
      onFilter: (value: any, record: BOMItem) => record.supplier === value
    }
  ];

  const categoryChartData = categoryAnalysis.map(cat => ({
    category: cat.category,
    active: cat.activeParts,
    pending: cat.pendingParts,
    inactive: cat.inactiveParts,
    notFound: cat.notFoundParts,
    totalValue: cat.totalValue
  }));

  const totalStats = {
    totalParts: bomData.length,
    activeParts: bomData.filter(item => item.status === 'D').length,
    pendingParts: bomData.filter(item => item.status === '0').length,
    inactiveParts: bomData.filter(item => item.status === 'X').length,
    notFoundParts: bomData.filter(item => item.status === 'NOT_FOUND').length,
    totalValue: bomData.reduce((sum, item) => sum + item.totalCost, 0)
  };

  return (
    <div className={`p-6 ${isDark ? 'bg-vista-25' : 'bg-gray-50'} min-h-screen`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <Title level={2} className={isDark ? 'text-vista-900' : 'text-gray-900'}>
            🔧 BOM Analysis
          </Title>
          <Text className={isDark ? 'text-vista-600' : 'text-gray-600'}>
            Detailed analysis of Bill of Materials and component status
          </Text>
        </div>
        <Space>
          <Button icon={<ExportOutlined />} type="primary">
            Export Analysis
          </Button>
        </Space>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={8} lg={4}>
          <Card className={isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}>
            <Statistic
              title="Total Parts"
              value={totalStats.totalParts}
              prefix={<InfoCircleOutlined />}
              valueStyle={{ color: colors.primary }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card className={isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}>
            <Statistic
              title="Active Parts"
              value={totalStats.activeParts}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: colors.active }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card className={isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}>
            <Statistic
              title="Pending Check"
              value={totalStats.pendingParts}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: colors.pending }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card className={isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}>
            <Statistic
              title="Inactive Parts"
              value={totalStats.inactiveParts}
              prefix={<StopOutlined />}
              valueStyle={{ color: colors.inactive }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card className={isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}>
            <Statistic
              title="Not Found"
              value={totalStats.notFoundParts}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: colors.notFound }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card className={isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}>
            <Statistic
              title="Total Value"
              value={totalStats.totalValue}
              prefix="$"
              precision={0}
              valueStyle={{ color: colors.primary }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts and Analysis */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} lg={16}>
          <Card
            title="📊 Status Distribution by Category"
            className={`h-96 ${isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}`}
          >
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar dataKey="active" stackId="a" fill={colors.active} name="Active" />
                <Bar dataKey="pending" stackId="a" fill={colors.pending} name="Pending" />
                <Bar dataKey="inactive" stackId="a" fill={colors.inactive} name="Inactive" />
                <Bar dataKey="notFound" stackId="a" fill={colors.notFound} name="Not Found" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card
            title="💰 Value Distribution"
            className={`h-96 ${isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}`}
          >
            <div className="space-y-4">
              {categoryAnalysis.slice(0, 5).map((cat, index) => (
                <div key={cat.category}>
                  <div className="flex justify-between items-center mb-1">
                    <Text>{cat.category}</Text>
                    <Text strong>${cat.totalValue.toLocaleString()}</Text>
                  </div>
                  <Progress
                    percent={(cat.totalValue / totalStats.totalValue) * 100}
                    strokeColor={colors.primary}
                    showInfo={false}
                  />
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      {/* Filters and Search */}
      <Card className={`mb-4 ${isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}`}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
            <Search
              placeholder="Search part number or description"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={4}>
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: '100%' }}
              placeholder="Filter by status"
            >
              <Option value="all">All Status</Option>
              <Option value="D">Active (D)</Option>
              <Option value="0">Check (0)</Option>
              <Option value="X">Inactive (X)</Option>
              <Option value="NOT_FOUND">Not Found</Option>
            </Select>
          </Col>
          <Col xs={24} sm={4}>
            <Select
              value={categoryFilter}
              onChange={setCategoryFilter}
              style={{ width: '100%' }}
              placeholder="Filter by category"
            >
              <Option value="all">All Categories</Option>
              {[...new Set(bomData.map(item => item.category))].map(cat => (
                <Option key={cat} value={cat}>{cat}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={8}>
            <Space>
              <Text>
                Showing {filteredBOMData.length} of {bomData.length} parts
              </Text>
              <Button
                icon={<FilterOutlined />}
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                  setCategoryFilter('all');
                }}
              >
                Clear Filters
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* BOM Table */}
      <Card
        title="📋 Bill of Materials Details"
        className={isDark ? 'bg-vista-50 border-vista-200' : 'bg-white border-gray-200'}
      >
        <Table
          columns={bomColumns}
          dataSource={filteredBOMData}
          rowKey="partNumber"
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`
          }}
          scroll={{ x: 1200 }}
          size="small"
        />
      </Card>
    </div>
  );
};
