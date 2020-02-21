{
//=========Macro generated from canvas: c1/c1
//=========  (Tue Feb 17 11:08:38 2015) by ROOT version5.34/14
   TCanvas *c1 = new TCanvas("c1a", "c1a",602,135,765,687);
   c1->Range(0,0,1,1);
   c1->SetFillColor(0);
   c1->SetBorderMode(0);
   c1->SetBorderSize(2);
   c1->SetFrameBorderMode(0);
   TLine *line = new TLine(0.4743758,0.5150555,0.5190539,0.6656101);
   line->SetLineColor(2);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.4717477,0.5103011,0.4296978,0.3645008);
   line->SetLineColor(4);
   line->SetLineWidth(3);
   line->Draw();
   TCurlyLine *curlyline = new TCurlyLine(0.521682,0.6656101,0.6701708,0.7511886,0.02,0.01);
   curlyline->SetWavy();

   Int_t ci;   // for color index setting
   ci = TColor::GetColor("#009900");
   curlyline->SetLineColor(ci);
   curlyline->SetLineWidth(3);
   curlyline->Draw();
   curlyline = new TCurlyLine(0.4283837,0.362916,0.2982917,0.2662441,0.02,0.01);
   curlyline->SetWavy();

   ci = TColor::GetColor("#009900");
   curlyline->SetLineColor(ci);
   curlyline->SetLineWidth(3);
   curlyline->Draw();
   line = new TLine(0.4270696,0.3597464,0.4454665,0.1917591);
   line->SetLineColor(6);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.5177398,0.6656101,0.4770039,0.8431062);
   line->SetLineColor(6);
   line->SetLineWidth(3);
   line->Draw();

   TLatex *   tex1 = new TLatex(0.521682,0.5736926,"t");
   tex1->SetLineWidth(2);
   tex1->Draw();

   TLatex * tex2 = new TLatex(0.4178712,0.429477,"#bar{t}");
   tex2->SetLineWidth(2);
   tex2->Draw();

   TLatex *   texW1 = new TLatex(0.721682,0.7736926,"b");
   texW1->SetLineWidth(2);
   texW1->Draw();

   TLatex *   texW2 = new TLatex(0.321682,0.3736926,"#bar{b}");
   texW2->SetLineWidth(2);
   texW2->Draw();

   TLatex *   texW1 = new TLatex(0.621682,0.6736926,"W");
   texW1->SetLineWidth(2);
   texW1->Draw();

   TLatex *   texW2 = new TLatex(0.221682,0.2736926,"W");
   texW2->SetLineWidth(2);
   texW2->Draw();

   c1->Modified();
   c1->cd();
   c1->SetSelected(c1);
   c1->ToggleToolBar();
}
