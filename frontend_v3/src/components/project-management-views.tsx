'use client';
import * as React from 'react';

import { ActionPlan, Task } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Badge } from './ui/badge';
import { cn } from '@/lib/utils';
import { User } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './ui/accordion';

const getPriorityBadgeColor = (priority: 'High' | 'Medium' | 'Low') => {
  switch (priority) {
    case 'High':
      return 'bg-destructive text-destructive-foreground';
    case 'Medium':
      return 'bg-accent text-accent-foreground';
    case 'Low':
      return 'bg-secondary text-secondary-foreground';
    default:
      return 'bg-muted text-muted-foreground';
  }
};

const TaskItem = ({ task, onToggle }: { task: Task, onToggle: (id: string) => void }) => (
  <div className="flex items-start gap-4 p-4 border-b">
    <Checkbox
      id={`task-${task.id}`}
      checked={task.completed}
      onCheckedChange={() => onToggle(task.id)}
      className="mt-1"
    />
    <div className="grid gap-1.5 flex-1">
      <div className="flex items-center justify-between">
        <label
          htmlFor={`task-${task.id}`}
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          {task.title}
        </label>
        <Badge className={cn("text-xs", getPriorityBadgeColor(task.priority))}>{task.priority} Priority</Badge>
      </div>
      <p className="text-sm text-muted-foreground">{task.description}</p>
      {task.humanContribution && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
            <User className="h-3 w-3 text-accent"/>
            <strong>Human Contribution:</strong>
            <span>{task.humanContribution}</span>
        </div>
      )}
    </div>
  </div>
);

const ListView = ({ categorizedTasks, onToggleTask }: { categorizedTasks: ActionPlan['actionPlan'], onToggleTask: (id: string) => void }) => (
    <Accordion type="multiple" defaultValue={categorizedTasks.map(c => c.categoryTitle)}>
        {categorizedTasks.map(category => (
        <AccordionItem key={category.categoryTitle} value={category.categoryTitle}>
            <AccordionTrigger className="px-6 text-lg font-semibold">
            {category.categoryTitle}
            </AccordionTrigger>
            <AccordionContent className="p-0">
            <div className="border-t">
                {category.tasks.map(task => (
                <TaskItem key={task.id} task={task} onToggle={onToggleTask} />
                ))}
            </div>
            </AccordionContent>
        </AccordionItem>
        ))}
    </Accordion>
);

const KanbanCard = ({ task, onToggleTask }: { task: Task, onToggleTask: (id: string) => void }) => (
    <Card className="mb-4">
        <CardContent className="p-4">
             <div className="flex items-start gap-3">
                <Checkbox
                    id={`kanban-task-${task.id}`}
                    checked={task.completed}
                    onCheckedChange={() => onToggleTask(task.id)}
                    className="mt-1"
                />
                <div className="grid gap-1.5 flex-1">
                     <label
                        htmlFor={`kanban-task-${task.id}`}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                        {task.title}
                    </label>
                    <p className="text-xs text-muted-foreground">{task.description}</p>
                </div>
            </div>
            <div className="flex items-center justify-between mt-3">
                <Badge className={cn("text-xs", getPriorityBadgeColor(task.priority))}>{task.priority}</Badge>
                 {task.humanContribution && (
                    <div className="flex items-center gap-1 text-xs text-muted-foreground" title={`Human Contribution: ${task.humanContribution}`}>
                        <User className="h-3 w-3 text-accent"/>
                    </div>
                )}
            </div>
        </CardContent>
    </Card>
);

const KanbanView = ({ categorizedTasks, onToggleTask }: { categorizedTasks: ActionPlan['actionPlan'], onToggleTask: (id: string) => void }) => {
    const todoTasks = categorizedTasks.flatMap(c => c.tasks).filter(t => !t.completed);
    const doneTasks = categorizedTasks.flatMap(c => c.tasks).filter(t => t.completed);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
            <Card>
                <CardHeader>
                    <CardTitle>To Do</CardTitle>
                </CardHeader>
                <CardContent>
                    {todoTasks.map(task => <KanbanCard key={task.id} task={task} onToggleTask={onToggleTask} />)}
                </CardContent>
            </Card>
             <Card>
                <CardHeader>
                    <CardTitle>Done</CardTitle>
                </CardHeader>
                <CardContent>
                    {doneTasks.map(task => <KanbanCard key={task.id} task={task} onToggleTask={onToggleTask} />)}
                </CardContent>
            </Card>
        </div>
    );
};

const GanttView = ({ tasks }: { tasks: Task[] }) => {
  const today = new Date();
  const startDate = tasks.length > 0 ? new Date(Math.min(...tasks.map(t => new Date(t.startDate).getTime()))) : today;
  const endDate = tasks.length > 0 ? new Date(Math.max(...tasks.map(t => new Date(t.endDate).getTime()))) : new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);

  const totalDays = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24) + 1;

  const getMonthYear = (date: Date) => date.toLocaleString('default', { month: 'short', year: 'numeric' });

  const months = [];
  let currentMonth = new Date(startDate);
  while(currentMonth <= endDate) {
      months.push(new Date(currentMonth));
      currentMonth.setMonth(currentMonth.getMonth() + 1);
  }

  return (
    <div className="p-4 overflow-x-auto">
      <div className="relative grid gap-y-2" style={{ gridTemplateColumns: `150px repeat(${totalDays}, minmax(30px, 1fr))`}}>
        {/* Header */}
        <div className="sticky top-0 left-0 bg-background z-10 font-semibold p-2 border-b">Task</div>
        {Array.from({ length: totalDays }, (_, i) => {
            const date = new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000);
            return (
                <div key={i} className="text-center text-xs p-2 border-b border-l">
                    <div>{date.getDate()}</div>
                    <div className="text-muted-foreground">{date.toLocaleString('default', { month: 'short' })}</div>
                </div>
            )
        })}

        {/* Tasks */}
        {tasks.map(task => {
          const taskStart = new Date(task.startDate);
          const taskEnd = new Date(task.endDate);
          const startDay = Math.floor((taskStart.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
          const duration = Math.ceil((taskEnd.getTime() - taskStart.getTime()) / (1000 * 60 * 60 * 24)) + 1;
          
          return (
            <React.Fragment key={task.id}>
              <div className="sticky left-0 bg-background z-10 truncate p-2 border-b text-sm" title={task.title}>{task.title}</div>
              <div style={{ gridColumnStart: startDay + 2, gridColumnEnd: `span ${duration}` }} className="h-full flex items-center">
                 <div className="h-8 w-full rounded-md bg-primary/80 flex items-center px-2 text-primary-foreground text-xs truncate" title={task.title}>
                    {task.title}
                </div>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};


const BusinessModelCanvasView = ({ bmc }: { bmc: ActionPlan['businessModelCanvas'] }) => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 p-4 text-sm">
        <Card className="col-span-1">
            <CardHeader><CardTitle className="text-base">Key Partners</CardTitle></CardHeader>
            <CardContent><ul>{bmc.keyPartners.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
        </Card>
        <div className="col-span-1 flex flex-col gap-4">
             <Card>
                <CardHeader><CardTitle className="text-base">Key Activities</CardTitle></CardHeader>
                <CardContent><ul>{bmc.keyActivities.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
            </Card>
             <Card>
                <CardHeader><CardTitle className="text-base">Key Resources</CardTitle></CardHeader>
                <CardContent><ul>{bmc.keyResources.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
            </Card>
        </div>
        <Card className="col-span-1">
            <CardHeader><CardTitle className="text-base">Value Propositions</CardTitle></CardHeader>
            <CardContent><ul>{bmc.valuePropositions.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
        </Card>
        <div className="col-span-1 flex flex-col gap-4">
            <Card>
                <CardHeader><CardTitle className="text-base">Customer Relationships</CardTitle></CardHeader>
                <CardContent><ul>{bmc.customerRelationships.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
            </Card>
            <Card>
                <CardHeader><CardTitle className="text-base">Channels</CardTitle></CardHeader>
                <CardContent><ul>{bmc.channels.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
            </Card>
        </div>
        <Card className="col-span-1">
            <CardHeader><CardTitle className="text-base">Customer Segments</CardTitle></CardHeader>
            <CardContent><ul>{bmc.customerSegments.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
        </Card>
        <Card className="col-span-1 lg:col-span-3 xl:col-span-3">
             <CardHeader><CardTitle className="text-base">Cost Structure</CardTitle></CardHeader>
            <CardContent><ul>{bmc.costStructure.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
        </Card>
        <Card className="col-span-1 lg:col-span-2 xl:col-span-2">
             <CardHeader><CardTitle className="text-base">Revenue Streams</CardTitle></CardHeader>
            <CardContent><ul>{bmc.revenueStreams.map((item, i) => <li key={i} className="mb-2 p-2 bg-muted/50 rounded-md">{item}</li>)}</ul></CardContent>
        </Card>
    </div>
);


export function ProjectManagementViews({ actionPlan, view, tasks, onToggleTask }: {
    actionPlan: ActionPlan;
    view: 'list' | 'kanban' | 'gantt' | 'canvas';
    tasks?: Task[];
    onToggleTask?: (id: string) => void;
}) {

    const getCategorizedTasks = () => {
        if (!tasks) return actionPlan.actionPlan;
        return actionPlan.actionPlan.map(category => ({
          ...category,
          tasks: category.tasks.map(task => tasks.find(t => t.id === task.id) || task),
        }));
    };
    
    switch (view) {
        case 'list':
            return <ListView categorizedTasks={getCategorizedTasks()} onToggleTask={onToggleTask!} />;
        case 'kanban':
            return <KanbanView categorizedTasks={getCategorizedTasks()} onToggleTask={onToggleTask!} />;
        case 'gantt':
            return <GanttView tasks={tasks || actionPlan.actionPlan.flatMap(c => c.tasks)} />;
        case 'canvas':
            return <BusinessModelCanvasView bmc={actionPlan.businessModelCanvas} />;
        default:
            return null;
    }
}
