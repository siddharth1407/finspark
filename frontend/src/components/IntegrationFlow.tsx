/**
 * Integration Flow Diagram Component
 * Interactive visualization of service integrations using React Flow
 */
import { useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import { motion } from 'framer-motion';

interface Service {
  service_type: string;
  service_name: string;
  priority: string;
  api_endpoints?: Array<{ method: string; path: string }>;
}

interface IntegrationFlowProps {
  services: Service[];
  projectName?: string;
}

// Custom node component
function ServiceNode({ data }: { data: any }) {
  const typeColors: Record<string, string> = {
    kyc: 'from-green-500 to-emerald-600',
    payment: 'from-blue-500 to-indigo-600',
    gst: 'from-yellow-500 to-orange-600',
    banking: 'from-purple-500 to-violet-600',
    default: 'from-gray-500 to-slate-600'
  };

  const bgColor = typeColors[data.type] || typeColors.default;

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.05 }}
      className={`bg-gradient-to-br ${bgColor} rounded-xl p-4 shadow-lg min-w-[180px] text-white`}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl">{data.icon}</span>
        <div>
          <h4 className="font-bold text-sm">{data.label}</h4>
          <span className={`text-xs px-2 py-0.5 rounded-full ${data.priority === 'mandatory' ? 'bg-red-500/50' : 'bg-gray-500/50'
            }`}>
            {data.priority}
          </span>
        </div>
      </div>
      {data.endpoints && data.endpoints.length > 0 && (
        <div className="text-xs mt-2 space-y-1 bg-black/20 rounded p-2">
          {data.endpoints.slice(0, 2).map((ep: any, i: number) => (
            <div key={i} className="flex items-center gap-1">
              <span className={`px-1 rounded text-[10px] font-bold ${ep.method === 'POST' ? 'bg-green-600' :
                ep.method === 'GET' ? 'bg-blue-600' : 'bg-yellow-600'
                }`}>
                {ep.method}
              </span>
              <span className="truncate">{ep.path}</span>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}

// Central orchestrator node
function OrchestratorNode({ data }: { data: any }) {
  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-full p-6 shadow-xl text-white text-center"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        className="text-3xl mb-1"
      >
        ⚡
      </motion.div>
      <h4 className="font-bold text-sm">{data.label}</h4>
      <p className="text-xs text-gray-300">Orchestrator</p>
    </motion.div>
  );
}

// Client app node
function ClientNode({ data }: { data: any }) {
  return (
    <motion.div
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="bg-gradient-to-br from-slate-700 to-slate-900 rounded-xl p-4 shadow-lg text-white"
    >
      <div className="text-2xl mb-1">📱</div>
      <h4 className="font-bold text-sm">{data.label}</h4>
      <p className="text-xs text-gray-400">Frontend App</p>
    </motion.div>
  );
}

const nodeTypes = {
  service: ServiceNode,
  orchestrator: OrchestratorNode,
  client: ClientNode,
};

const serviceIcons: Record<string, string> = {
  kyc: '🪪',
  payment: '💳',
  gst: '📋',
  banking: '🏦',
  default: '🔧'
};

export function IntegrationFlow({ services, projectName = 'Integration' }: IntegrationFlowProps) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    // Client node (left)
    nodes.push({
      id: 'client',
      type: 'client',
      position: { x: 50, y: 200 },
      data: { label: 'Client App' },
    });

    // Orchestrator node (center)
    nodes.push({
      id: 'orchestrator',
      type: 'orchestrator',
      position: { x: 300, y: 200 },
      data: { label: projectName },
    });

    // Edge from client to orchestrator
    edges.push({
      id: 'e-client-orch',
      source: 'client',
      target: 'orchestrator',
      animated: true,
      style: { stroke: '#6366f1', strokeWidth: 3 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#6366f1' },
      label: 'API Request',
      labelStyle: { fill: '#9ca3af', fontSize: 10 },
    });

    // Service nodes (right side, arranged in a fan)
    services.forEach((service, index) => {
      const totalServices = services.length;
      const angleRange = Math.PI * 0.8; // 144 degrees
      const startAngle = -angleRange / 2;
      const angle = startAngle + (angleRange * index) / (totalServices - 1 || 1);

      const radius = 250;
      const x = 550 + Math.cos(angle) * radius * 0.3;
      const y = 200 + Math.sin(angle) * radius;

      const nodeId = `service-${index}`;

      nodes.push({
        id: nodeId,
        type: 'service',
        position: { x, y },
        data: {
          label: service.service_name,
          type: service.service_type,
          priority: service.priority,
          icon: serviceIcons[service.service_type] || serviceIcons.default,
          endpoints: service.api_endpoints,
        },
      });

      // Edge from orchestrator to service
      edges.push({
        id: `e-orch-${nodeId}`,
        source: 'orchestrator',
        target: nodeId,
        animated: true,
        style: {
          stroke: service.priority === 'mandatory' ? '#ef4444' : '#6b7280',
          strokeWidth: 2
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: service.priority === 'mandatory' ? '#ef4444' : '#6b7280'
        },
      });
    });

    return { nodes, edges };
  }, [services, projectName]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-[500px] bg-slate-900 rounded-xl overflow-hidden border border-slate-700">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.5}
        maxZoom={1.5}
      >
        <Background color="#334155" gap={20} />
        <Controls className="bg-slate-800 border-slate-600" />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'orchestrator') return '#6366f1';
            if (node.type === 'client') return '#475569';
            return '#10b981';
          }}
          className="bg-slate-800 border-slate-600"
        />
      </ReactFlow>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-slate-800/90 backdrop-blur rounded-lg p-3 text-xs text-white">
        <div className="font-semibold mb-2">Legend</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span>Mandatory Service</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-500" />
            <span>Optional Service</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-indigo-500" />
            <span>Data Flow</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default IntegrationFlow;
