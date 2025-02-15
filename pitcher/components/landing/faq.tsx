import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
  } from "@/components/ui/accordion";
  
  const Faq1 = () => {
    const faqs = [
      {
        question: "How does Pitcher analyze my codebase?",
        answer:
          "Pitcher uses advanced AI to analyze your GitHub repository, documentation, and project files. It understands your code structure, features, and technical specifications to create relevant and accurate presentations.",
      },
      {
        question: "Can I customize the generated presentations?",
        answer:
          "Yes! While Pitcher automatically generates your initial presentation, you have full control to edit, customize, and refine the content, design, and structure to match your needs.",
      },
      {
        question: "What types of voice models are available?",
        answer:
          "Pitcher offers a variety of natural-sounding AI voice models in multiple languages and accents. You can choose the voice that best represents your brand and presentation style.",
      },
      {
        question: "How accurate is the Q&A feature?",
        answer:
          "Our AI is trained on your specific project data, ensuring highly accurate and contextual responses to audience questions. The system continuously learns and improves based on interactions.",
      },
    ];
  
    return (
      <section className="py-32">
        <div className="container">
          <h1 className="mb-4 text-3xl font-semibold md:mb-11 md:text-5xl">
            Frequently asked questions
          </h1>
          {faqs.map((faq, index) => (
            <Accordion key={index} type="single" collapsible>
              <AccordionItem value={`item-${index}`}>
                <AccordionTrigger className="hover:text-foreground/60 hover:no-underline">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent>{faq.answer}</AccordionContent>
              </AccordionItem>
            </Accordion>
          ))}
        </div>
      </section>
    );
  };
  
  export default Faq1;
  