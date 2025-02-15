import os
import json
from pathlib import Path
import openai
from typing import List, Dict, Tuple
import time
from datetime import datetime
import asyncio
import aiohttp
from openai import AsyncOpenAI

class StartupDataGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)
        
    def get_subsections(self) -> Dict[str, List[Tuple[str, str]]]:
        """Returns a dictionary of section names and their subsections with prompts."""
        return {
            "company_info": [
                ("name_and_branding", "Create a detailed company name and branding guide. Include the name's meaning, logo concept, color scheme, and brand voice. Explain how each element reflects the company's mission."),
                ("mission_and_vision", "Write an extensive mission and vision statement. Include long-term goals, core purpose, and how the company aims to transform its industry."),
                ("founding_story", "Create a compelling founding story. Include the founders' backgrounds, the moment of inspiration, early challenges, and key decisions that shaped the company."),
                ("company_culture", "Detail the company culture, values, and work environment. Include team traditions, communication style, work-life balance philosophy, and employee development programs."),
                ("team_structure", "Create a comprehensive team structure. Include key roles, reporting relationships, required expertise, and how the team will scale."),
                ("physical_presence", "Describe the company's physical and digital presence. Include office layout, remote work policy, and how the physical/digital spaces reflect company values."),
                ("diversity_inclusion", "Detail the company's approach to diversity, equity, and inclusion. Include specific initiatives, goals, and measurement metrics."),
                ("sustainability", "Outline the company's environmental and social responsibility initiatives. Include sustainability goals and implementation strategies."),
                ("governance", "Define the company's governance structure, board composition, and decision-making processes.")
            ],
            "problem": [
                ("problem_overview", "Provide a comprehensive overview of the core problem. Include historical context and why previous solutions have failed."),
                ("user_impact", "Detail how this problem affects different user groups. Include personal stories, daily challenges, and emotional impact."),
                ("market_research", "Present detailed market research about the problem. Include statistics, trends, and academic/industry studies."),
                ("hidden_costs", "Analyze the hidden costs and ripple effects of this problem. Include both tangible and intangible impacts on society."),
                ("current_solutions", "Evaluate current solutions and their limitations. Include detailed analysis of why they fall short."),
                ("future_implications", "Explore how this problem might evolve in the future if not addressed. Include potential societal impacts."),
                ("stakeholder_analysis", "Identify and analyze all stakeholders affected by the problem. Include their perspectives and needs."),
                ("geographic_impact", "Analyze how the problem varies across different geographic regions and cultures."),
                ("demographic_factors", "Examine how different demographic groups are affected by the problem.")
            ],
            "solution": [
                ("technical_architecture", "Detail the complete technical architecture of the solution. Include systems, integrations, and technology stack."),
                ("user_experience", "Create a comprehensive user journey map. Include all touchpoints, features, and interaction patterns."),
                ("feature_breakdown", "Provide an extensive breakdown of all features and capabilities. Include use cases and technical requirements."),
                ("innovation_aspects", "Detail the innovative aspects of the solution. Include proprietary technology and methodologies."),
                ("implementation_plan", "Create a detailed implementation and rollout plan. Include phases, timelines, and technical requirements."),
                ("scalability", "Analyze the scalability aspects of the solution. Include technical architecture and growth capabilities."),
                ("security_privacy", "Detail the security and privacy measures implemented in the solution. Include compliance and data protection strategies."),
                ("accessibility", "Outline how the solution ensures accessibility for all users. Include compliance with standards and inclusive design principles."),
                ("integration_capabilities", "Describe the solution's integration capabilities with other systems and platforms."),
                ("maintenance_support", "Detail the maintenance and support structure for the solution.")
            ],
            "metrics": [
                ("user_growth", "Project detailed user growth metrics. Include acquisition channels, retention rates, and engagement patterns."),
                ("revenue_streams", "Break down all potential revenue streams. Include pricing models and revenue projections."),
                ("customer_satisfaction", "Detail customer satisfaction metrics and measurement methods. Include NPS scores and feedback systems."),
                ("operational_efficiency", "Analyze operational efficiency metrics. Include cost structures and optimization strategies."),
                ("market_penetration", "Project market penetration rates and strategies. Include regional expansion plans."),
                ("performance_indicators", "Define key performance indicators. Include measurement methods and targets."),
                ("churn_analysis", "Detail methods for measuring and reducing customer churn. Include predictive indicators."),
                ("viral_coefficients", "Calculate and track viral growth metrics and referral success rates."),
                ("unit_economics", "Break down unit economics including CAC, LTV, and payback period."),
                ("social_impact", "Measure and track the solution's social impact and community benefits.")
            ],
            "business_strategy": [
                ("revenue_model", "Create a detailed revenue model. Include pricing strategy, payment systems, and revenue projections."),
                ("marketing_strategy", "Develop a comprehensive marketing strategy. Include channels, messaging, and campaign structures."),
                ("partnership_strategy", "Detail potential partnerships and collaboration opportunities. Include partner selection criteria."),
                ("growth_strategy", "Create a detailed growth and expansion strategy. Include market entry plans and scaling approaches."),
                ("competitive_strategy", "Analyze competitive positioning and defense strategies. Include market differentiation tactics."),
                ("risk_mitigation", "Identify potential risks and mitigation strategies. Include contingency plans."),
                ("international_expansion", "Plan the international expansion strategy including market selection and localization."),
                ("product_roadmap", "Define the long-term product development roadmap and feature priorities."),
                ("acquisition_strategy", "Outline potential acquisition targets and integration strategies."),
                ("exit_strategy", "Detail possible exit strategies including IPO and M&A scenarios.")
            ],
            "market_analysis": [
                ("market_size", "Calculate total addressable market size. Include detailed segmentation and growth projections."),
                ("competitor_analysis", "Provide detailed analysis of competitors. Include strengths, weaknesses, and market positions."),
                ("market_trends", "Analyze current and emerging market trends. Include technology and consumer behavior shifts."),
                ("regulatory_environment", "Examine regulatory environment and compliance requirements. Include potential future regulations."),
                ("market_barriers", "Analyze market entry barriers and challenges. Include strategies to overcome them."),
                ("market_opportunities", "Identify untapped market opportunities. Include potential expansion areas."),
                ("customer_segments", "Define and analyze detailed customer segments and their specific needs."),
                ("channel_analysis", "Evaluate different distribution channels and their effectiveness."),
                ("regional_variations", "Analyze how market conditions vary across different regions."),
                ("technology_landscape", "Map the current and emerging technology landscape affecting the market.")
            ],
            "financial_planning": [
                ("funding_requirements", "Break down detailed funding requirements. Include allocation plans and milestones."),
                ("financial_projections", "Create detailed financial projections. Include revenue, costs, and profitability analysis."),
                ("cash_flow", "Analyze cash flow requirements and management. Include working capital needs."),
                ("investment_returns", "Project investment returns and exit strategies. Include valuation models."),
                ("cost_structure", "Break down cost structure and optimization strategies. Include fixed and variable costs."),
                ("pricing_strategy", "Develop detailed pricing strategy. Include market positioning and competitive analysis."),
                ("tax_planning", "Detail tax optimization strategies and compliance requirements."),
                ("fundraising_strategy", "Outline the fundraising strategy including timing and investor targeting."),
                ("financial_risks", "Identify and analyze potential financial risks and mitigation strategies."),
                ("asset_management", "Plan for managing and optimizing company assets and resources.")
            ]
        }

    async def generate_subsection(self, idea: str, section: str, subsection: Tuple[str, str], session_dir: Path) -> Dict:
        """Generate detailed content for a specific subsection."""
        subsection_name, subsection_prompt = subsection
        
        system_prompt = f"""You are a startup expert focusing specifically on {section} - {subsection_name}. 
        Generate an extremely detailed, well-researched response. Include specific numbers, examples, and detailed analysis. 
        Write in a professional, thorough style. WRITE AS MUCH AS POSSIBLE. Make up statistics if needed.  write as much as you can"""
        
        prompt = f"""For this startup idea: {idea}

{subsection_prompt}

Be extremely specific and detailed. Include:
- Specific numbers and metrics where relevant
- Detailed examples and use cases
- Industry-specific insights
- Implementation details
- Future projections and growth plans
- Specific challenges and solutions
- Concrete action items and recommendations

Write a comprehensive, well-structured response that could serve as a standalone document."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2500
            )
            
            # Save the raw response text
            content = response.choices[0].message.content
            
            # Create section directory
            section_dir = session_dir / section
            section_dir.mkdir(exist_ok=True)
            
            # Save subsection file
            filename = f"{subsection_name}.txt"
            filepath = section_dir / filename
            with open(filepath, "w") as f:
                f.write(f"{section.upper()} - {subsection_name.replace('_', ' ').upper()}\n")
                f.write("="*80 + "\n\n")
                f.write(content)
            
            print(f"Generated and saved {section}/{subsection_name}")
            return {f"{section}/{subsection_name}": content}
            
        except Exception as e:
            print(f"Error generating {section}/{subsection_name}: {str(e)}")
            return {f"{section}/{subsection_name}": f"Error: {str(e)}"}

    async def generate_all_subsections(self, idea: str, session_dir: Path) -> Dict:
        """Generate all subsections concurrently."""
        tasks = []
        subsections = self.get_subsections()
        
        for section, section_subsections in subsections.items():
            for subsection in section_subsections:
                task = asyncio.create_task(
                    self.generate_subsection(idea, section, subsection, session_dir)
                )
                tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_data = {}
        for result in results:
            if isinstance(result, dict):
                all_data.update(result)
        
        return all_data

    async def generate_and_save_startup_data(self, idea: str) -> Dict:
        # Create data directory and session directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_dir = Path("data")
        session_dir = data_dir / f"session_{timestamp}_{idea.lower().replace(' ', '_')[:50]}"
        data_dir.mkdir(exist_ok=True)
        session_dir.mkdir(exist_ok=True)
        
        print("\nGenerating all sections and subsections in parallel...")
        all_data = await self.generate_all_subsections(idea, session_dir)
        
        # Save complete data to index file
        index_filepath = session_dir / "complete_analysis.txt"
        
        # Create index document
        with open(index_filepath, "w") as f:
            f.write(f"Complete Startup Analysis for: {idea}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for section, subsections in self.get_subsections().items():
                f.write(f"\n{'='*80}\n")
                f.write(f"{section.upper()}\n")
                f.write(f"{'='*80}\n\n")
                
                for subsection_name, _ in subsections:
                    key = f"{section}/{subsection_name}"
                    content = all_data.get(key, "Content not generated")
                    f.write(f"\n{'-'*40}\n")
                    f.write(f"{subsection_name.replace('_', ' ').upper()}\n")
                    f.write(f"{'-'*40}\n\n")
                    f.write(content + "\n")
        
        print(f"\nAll sections generated and saved to: {session_dir}")
        print(f"Complete analysis document: {index_filepath}")
        
        return all_data

async def main_async():
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    
    # Initialize generator
    generator = StartupDataGenerator(api_key)
    
    # Get input from user
    idea = "A website that takes in user's journal entries and gives AI summaries for each, allows for sentinent analysis and mood tracking, and gives song recommendation. "
    
    # Generate and save data
    print("\nGenerating detailed startup analysis...")
    all_data = await generator.generate_and_save_startup_data(idea)
    
    if not all_data:
        print("\nNo data was generated.")
    else:
        print("\nSuccessfully generated all sections and subsections!")
        print("Check the output directory for the complete analysis and individual files.")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
