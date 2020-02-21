{
//=========Macro generated from canvas: c2/c2
//=========  (Tue Feb 17 11:58:46 2015) by ROOT version5.34/14
   TCanvas *c2 = new TCanvas("c2", "c2",605,219,790,777);
   c2->Range(0,0,1,1);
   c2->SetFillColor(0);
   c2->SetBorderMode(0);
   c2->SetBorderSize(2);
   c2->SetFrameBorderMode(0);
   TLine *line = new TLine(0.4743758,0.5150555,0.5190539,0.6656101);
   line->SetLineColor(2);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.4730618,0.5108538,0.4296978,0.3645008);
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
   TLatex *   tex = new TLatex(0.521682,0.5736926,"t");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.4178712,0.429477,"#bar{t}");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.455979,0.7276853,"b");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.4599212,0.2586989,"#bar{b}");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.6057819,0.6520424,"W");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.3127464,0.3373676,"W");
   tex->SetLineWidth(2);
   tex->Draw();
   line = new TLine(0.6714849,0.7510854,0.8370565,0.7308249);

   ci = TColor::GetColor("#ff6600");
   line->SetLineColor(ci);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.6701708,0.7510854,0.7017083,0.9146165);

   ci = TColor::GetColor("#ff6600");
   line->SetLineColor(ci);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.2969777,0.2648336,0.2667543,0.09985528);

   ci = TColor::GetColor("#0099ff");
   line->SetLineColor(ci);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.2969777,0.2633864,0.1498029,0.2199711);

   ci = TColor::GetColor("#0099ff");
   line->SetLineColor(ci);
   line->SetLineWidth(3);
   line->Draw();

   TMarker *marker = new TMarker(0.4743758,0.5094067,29);
   ci = TColor::GetColor("#ffcc00");
   marker->SetMarkerColor(ci);
   marker->SetMarkerStyle(29);
   marker->SetMarkerSize(3);
   marker->Draw();

   tex = new TLatex(0.662116,0.9334258,"\\ell");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.8498294,0.6948682,"#nu");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.2116041,0.07905687,"q'");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.1006826,0.1983356,"#bar{q}");
   tex->SetLineWidth(2);
   tex->Draw();
   c2->Modified();
   c2->cd();
   c2->SetSelected(c2);
   c2->ToggleToolBar();

   c2->Print("c2.png");
   
}
