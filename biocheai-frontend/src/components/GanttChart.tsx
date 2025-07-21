import React from 'react';
import { FrappeGantt, ViewMode, Task as FrappeTask } from 'frappe-gantt-react';
import { Task, TimelineData } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Calendar, Clock, Users } from 'lucide-react';

interface GanttChartProps {
  timelineData: TimelineData;
  onTaskClick?: (task: Task) => void;
  onTaskUpdate?: (taskId: string, start: Date, end: Date) => void;
}

const GanttChart: React.FC<GanttChartProps> = ({ 
  timelineData, 
  onTaskClick, 
  onTaskUpdate 
}) => {
  const ganttTasks = timelineData.tasks
    .filter(task => task.start_date && task.end_date)
    .map(task => {
      const ganttTask = new FrappeTask({
        id: task.id,
        name: task.title,
        start: task.start_date,
        end: task.end_date,
        progress: task.progress_percentage || 0,
        custom_class: `priority-${task.priority} status-${task.status}`
      });
      
      if (task.dependencies?.length) {
        ganttTask.setDependencies(task.dependencies.map(dep => dep.depends_on_task_id));
      }
      
      return ganttTask;
    });

  const handleTaskChange = (task: any) => {
    if (onTaskUpdate) {
      onTaskUpdate(task.id, new Date(task.start), new Date(task.end));
    }
  };

  const handleTaskClick = (task: any) => {
    const originalTask = timelineData.tasks.find(t => t.id === task.id);
    if (originalTask && onTaskClick) {
      onTaskClick(originalTask);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="h-5 w-5" />
            <span>Project Timeline</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="gantt-container">
            {ganttTasks.length > 0 ? (
              <FrappeGantt
                tasks={ganttTasks}
                viewMode={ViewMode.Month}
                onClick={handleTaskClick}
                onDateChange={handleTaskChange}
              />
            ) : (
              <div className="text-center py-8">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Create tasks to visualize your project timeline
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Milestones Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Clock className="h-5 w-5" />
            <span>Milestones</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {timelineData.milestones && timelineData.milestones.length > 0 ? (
              timelineData.milestones
                .filter(milestone => milestone.due_date)
                .map(milestone => (
                  <div key={milestone.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        milestone.status === 'achieved' ? 'bg-green-500' :
                        milestone.status === 'overdue' ? 'bg-red-500' : 'bg-yellow-500'
                      }`} />
                      <div>
                        <h4 className="font-medium">{milestone.title}</h4>
                        <p className="text-sm text-gray-500">
                          Due: {new Date(milestone.due_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={milestone.status === 'achieved' ? 'default' : 'secondary'}>
                        {milestone.completion_percentage || 0}% Complete
                      </Badge>
                      <Badge variant="outline">
                        {milestone.status}
                      </Badge>
                    </div>
                  </div>
                ))
            ) : (
              <div className="text-center py-8">
                <Clock className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No milestones yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Create milestones to track important project deadlines
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Resource Allocation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Resource Allocation</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Resource tracking</h3>
            <p className="mt-1 text-sm text-gray-500">
              Team capacity and workload distribution will appear here
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GanttChart;
