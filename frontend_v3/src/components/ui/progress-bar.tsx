'use client';
import * as React from 'react';

import { cn } from "@/lib/utils";

interface StepProgressBarProps {
  steps: string[];
  currentStep: number;
}

export const StepProgressBar = ({ steps, currentStep }: StepProgressBarProps) => {
  return (
    <div className="flex items-center justify-between w-full max-w-2xl mx-auto mt-8">
      {steps.map((step, index) => {
        const isActive = index <= currentStep;
        const isCompleted = index < currentStep;

        return (
          <React.Fragment key={step}>
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  "flex items-center justify-center w-8 h-8 rounded-full border-2 transition-colors duration-300",
                  isActive ? "bg-primary border-primary" : "bg-card border-border"
                )}
              >
                <div
                  className={cn(
                    "w-4 h-4 rounded-full transition-colors duration-300",
                    isCompleted ? "bg-primary-foreground" : (isActive ? "bg-primary" : "bg-card")
                  )}
                />
              </div>
              <p
                className={cn(
                  "mt-2 text-sm text-center font-medium transition-colors duration-300",
                  isActive ? "text-primary" : "text-muted-foreground"
                )}
              >
                {step}
              </p>
            </div>
            {index < steps.length - 1 && (
              <div className="flex-1 h-1 mx-2">
                <div className="w-full h-full bg-border rounded-full relative">
                    <div
                        className="absolute top-0 left-0 h-full bg-primary rounded-full transition-all duration-500"
                        style={{ width: `${isCompleted ? 100 : (isActive ? 50 : 0)}%` }}
                    />
                </div>
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
